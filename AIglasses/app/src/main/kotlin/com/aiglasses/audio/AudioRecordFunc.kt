package com.aiglasses.audio

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import com.aiglasses.audio.AudioFileFunc.getFileSize
import com.aiglasses.audio.AudioFileFunc.isSdcardExit
import com.aiglasses.audio.AudioFileFunc.rawFilePath
import com.aiglasses.audio.AudioFileFunc.wavFilePath
import com.aiglasses.audio.Recorder.THRESH_HOLD_DB
import java.io.File
import java.io.FileInputStream
import java.io.FileNotFoundException
import java.io.FileOutputStream
import java.io.IOException
import kotlin.math.abs

object AudioRecordFunc {
    // 缓冲区字节大小
    private var bufferSizeInBytes = 0

    //AudioName裸音频数据文件 ，麦克风
    private var AudioName = ""

    //NewAudioName可播放的音频文件
    private var NewAudioName = ""
    private var audioRecord: AudioRecord? = null
    private var isRecord = false // 设置正在录制的状态
    fun startRecordAndFile(): Int {
        //判断是否有外部存储设备sdcard
        return if (isSdcardExit) {
            if (isRecord) {
                ErrorCode.E_STATE_RECODING
            } else {
                if (audioRecord == null) creatAudioRecord()
                audioRecord!!.startRecording()
                // 让录制状态为true
                isRecord = true
                // 开启音频文件写入线程
                Thread(AudioRecordThread()).start()
                ErrorCode.SUCCESS
            }
        } else {
            ErrorCode.E_NOSDCARD
        }
    }

    fun getVolume(): Int {
//        throw NotImplementedError()
        return THRESH_HOLD_DB
    }

    fun stopRecordAndFile() {
        close()
    }

    val recordFileSize: Long
        get() = getFileSize(NewAudioName)

    private fun close() {
        if (audioRecord != null) {
            println("stopRecord")
            isRecord = false //停止文件写入
            audioRecord!!.stop()
            audioRecord!!.release() //释放资源
            audioRecord = null
        }
    }

    @SuppressLint("MissingPermission")
    private fun creatAudioRecord() {
        // 获取音频文件路径
        AudioName = rawFilePath
        NewAudioName = wavFilePath

        // 获得缓冲区字节大小
        bufferSizeInBytes = AudioRecord.getMinBufferSize(
            AudioFileFunc.AUDIO_SAMPLE_RATE,
            AudioFormat.CHANNEL_IN_STEREO, AudioFormat.ENCODING_PCM_16BIT
        )

        audioRecord = AudioRecord(
            AudioFileFunc.AUDIO_INPUT, AudioFileFunc.AUDIO_SAMPLE_RATE,
            AudioFormat.CHANNEL_IN_STEREO, AudioFormat.ENCODING_PCM_16BIT, bufferSizeInBytes
        )
    }

    class AudioRecordThread : Runnable {
        override fun run() {
            writeDateTOFile() //往文件中写入裸数据
            copyWaveFile(AudioName, NewAudioName) //给裸数据加上头文件
        }
    }

    /**
     * 这里将数据写入文件，但是并不能播放，因为AudioRecord获得的音频是原始的裸音频，
     * 如果需要播放就必须加入一些格式或者编码的头信息。但是这样的好处就是你可以对音频的 裸数据进行处理，比如你要做一个爱说话的TOM
     * 猫在这里就进行音频的处理，然后重新封装 所以说这样得到的音频比较容易做一些音频的处理。
     */
    private fun writeDateTOFile() {
        // new一个byte数组用来存一些字节数据，大小为缓冲区大小
        val audiodata = ByteArray(bufferSizeInBytes)
        var fos: FileOutputStream? = null
        try {
            val file = File(AudioName)
            if (file.exists()) {
                file.delete()
            }
            fos = FileOutputStream(file) // 建立一个可存取字节的文件
        } catch (e: Exception) {
            e.printStackTrace()
        }
        while (isRecord) {
            val readSize = audioRecord!!.read(audiodata, 0, bufferSizeInBytes)
            if (AudioRecord.ERROR_INVALID_OPERATION != readSize && fos != null) {
                try {

                    var maxAmplitude = 0
                    for (i in 0 until readSize) {
                        val amplitude: Int = abs(audiodata[i].toInt())
                        if (amplitude > maxAmplitude) {
                            maxAmplitude = amplitude
                        }
                    }

                    fos.write(audiodata)
                } catch (e: IOException) {
                    e.printStackTrace()
                }
            }
        }
        try {
            fos?.close() // 关闭写入流
        } catch (e: IOException) {
            e.printStackTrace()
        }
    }

    // 这里得到可播放的音频文件
    private fun copyWaveFile(inFilename: String, outFilename: String) {

        val longSampleRate = AudioFileFunc.AUDIO_SAMPLE_RATE.toLong()
        val channels = 2
        val byteRate = (16 * AudioFileFunc.AUDIO_SAMPLE_RATE * channels / 8).toLong()
        val data = ByteArray(bufferSizeInBytes)
        try {
            val inStream = FileInputStream(inFilename)
            val outStream = FileOutputStream(outFilename)
            val totalAudioLen = inStream.channel.size()
            val totalDataLen = totalAudioLen + 36
            writeWaveFileHeader(
                outStream, totalAudioLen, totalDataLen,
                longSampleRate, channels, byteRate
            )
            while (inStream.read(data) != -1) {
                outStream.write(data)
            }
            inStream.close()
            outStream.close()
        } catch (e: FileNotFoundException) {
            e.printStackTrace()
        } catch (e: IOException) {
            e.printStackTrace()
        }
    }

    /**
     * 这里提供一个头信息。插入这些信息就可以得到可以播放的文件。
     * 为我为啥插入这44个字节，这个还真没深入研究，不过你随便打开一个wav
     * 音频的文件，可以发现前面的头文件可以说基本一样哦。每种格式的文件都有
     * 自己特有的头文件。
     */
    @Throws(IOException::class)
    private fun writeWaveFileHeader(
        out: FileOutputStream, totalAudioLen: Long,
        totalDataLen: Long, longSampleRate: Long, channels: Int, byteRate: Long
    ) {
        val header = ByteArray(44)
        header[0] = 'R'.code.toByte() // RIFF/WAVE header
        header[1] = 'I'.code.toByte()
        header[2] = 'F'.code.toByte()
        header[3] = 'F'.code.toByte()
        header[4] = (totalDataLen and 0xffL).toByte()
        header[5] = (totalDataLen shr 8 and 0xffL).toByte()
        header[6] = (totalDataLen shr 16 and 0xffL).toByte()
        header[7] = (totalDataLen shr 24 and 0xffL).toByte()
        header[8] = 'W'.code.toByte()
        header[9] = 'A'.code.toByte()
        header[10] = 'V'.code.toByte()
        header[11] = 'E'.code.toByte()
        header[12] = 'f'.code.toByte() // 'fmt ' chunk
        header[13] = 'm'.code.toByte()
        header[14] = 't'.code.toByte()
        header[15] = ' '.code.toByte()
        header[16] = 16 // 4 bytes: size of 'fmt ' chunk
        header[17] = 0
        header[18] = 0
        header[19] = 0
        header[20] = 1 // format = 1
        header[21] = 0
        header[22] = channels.toByte()
        header[23] = 0
        header[24] = (longSampleRate and 0xffL).toByte()
        header[25] = (longSampleRate shr 8 and 0xffL).toByte()
        header[26] = (longSampleRate shr 16 and 0xffL).toByte()
        header[27] = (longSampleRate shr 24 and 0xffL).toByte()
        header[28] = (byteRate and 0xffL).toByte()
        header[29] = (byteRate shr 8 and 0xffL).toByte()
        header[30] = (byteRate shr 16 and 0xffL).toByte()
        header[31] = (byteRate shr 24 and 0xffL).toByte()
        header[32] = (2 * 16 / 8).toByte() // block align
        header[33] = 0
        header[34] = 16 // bits per sample
        header[35] = 0
        header[36] = 'd'.code.toByte()
        header[37] = 'a'.code.toByte()
        header[38] = 't'.code.toByte()
        header[39] = 'a'.code.toByte()
        header[40] = (totalAudioLen and 0xffL).toByte()
        header[41] = (totalAudioLen shr 8 and 0xffL).toByte()
        header[42] = (totalAudioLen shr 16 and 0xffL).toByte()
        header[43] = (totalAudioLen shr 24 and 0xffL).toByte()
        out.write(header, 0, 44)
    }

}
