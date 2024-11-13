package com.aiglasses.audio

import android.media.MediaRecorder
import android.os.Environment
import java.io.File

object AudioFileFunc {
    //音频输入-麦克风
    const val AUDIO_INPUT = MediaRecorder.AudioSource.MIC

    //采用频率
    //44100是目前的标准，但是某些设备仍然支持22050，16000，11025
    const val AUDIO_SAMPLE_RATE = 44100 //44.1KHz,普遍使用的频率

    //录音输出文件
    private const val AUDIO_RAW_FILENAME = "RawAudio.raw"
    private const val AUDIO_WAV_FILENAME = "FinalAudio.wav"
    private const val AUDIO_AMR_FILENAME = "FinalAudio.amr"

    @JvmStatic
    val isSdcardExit: Boolean
        /**
         * 判断是否有外部存储设备sdcard
         * @return true | false
         */
        get() = Environment.getExternalStorageState() == Environment.MEDIA_MOUNTED

    @JvmStatic
    val rawFilePath: String
        /**
         * 获取麦克风输入的原始音频流文件路径
         * @return
         */
        get() {
            var mAudioRawPath = ""
            if (isSdcardExit) {
                val fileBasePath = Environment.getExternalStorageDirectory().absolutePath
                mAudioRawPath = "$fileBasePath/aiglasses/$AUDIO_RAW_FILENAME"
            }
            return mAudioRawPath
        }

    @JvmStatic
    val wavFilePath: String
        /**
         * 获取编码后的WAV格式音频文件路径
         * @return
         */
        get() {
            var mAudioWavPath = ""
            if (isSdcardExit) {
                val fileBasePath = Environment.getExternalStorageDirectory().absolutePath
                mAudioWavPath = "$fileBasePath/aiglasses/$AUDIO_WAV_FILENAME"
            }
            return mAudioWavPath
        }

    @JvmStatic
    val amrFilePath: String
        /**
         * 获取编码后的AMR格式音频文件路径
         * @return
         */
        get() {
            var mAudioAMRPath = ""
            if (isSdcardExit) {
                val fileBasePath = Environment.getExternalStorageDirectory().absolutePath
                mAudioAMRPath = "$fileBasePath/aiglasses/$AUDIO_AMR_FILENAME"
            }
            return mAudioAMRPath
        }

    /**
     * 获取文件大小
     * @param path,文件的绝对路径
     * @return
     */
    @JvmStatic
    fun getFileSize(path: String): Long {
        val mFile = File(path)
        return if (!mFile.exists()) -1 else mFile.length()
    }
}