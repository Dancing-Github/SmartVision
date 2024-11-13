package com.aiglasses.audio

import android.annotation.SuppressLint
import android.media.MediaRecorder
import com.aiglasses.audio.AudioFileFunc.amrFilePath
import com.aiglasses.audio.AudioFileFunc.getFileSize
import com.aiglasses.audio.AudioFileFunc.isSdcardExit
import java.io.File
import java.io.IOException

object MediaRecordFunc {
    private var isRecord = false
    private var mMediaRecorder: MediaRecorder? = null
    fun startRecordAndFile(): Int {
        //判断是否有外部存储设备sdcard
        return if (isSdcardExit) {
            if (isRecord) {
                ErrorCode.E_STATE_RECODING
            } else {
                if (mMediaRecorder == null) createMediaRecord()
                try {
                    mMediaRecorder!!.prepare()
                    mMediaRecorder!!.start()
                    // 让录制状态为true
                    isRecord = true
                    ErrorCode.SUCCESS
                } catch (ex: IOException) {
                    ex.printStackTrace()
                    ErrorCode.E_UNKOWN
                }
            }
        } else {
            ErrorCode.E_NOSDCARD
        }
    }

    fun getVolume(): Int {
        return mMediaRecorder?.maxAmplitude ?: 0
    }

    fun stopRecordAndFile() {
        close()
    }

    val recordFileSize: Long
        get() = getFileSize(amrFilePath)

    @SuppressLint("MissingPermission")
    private fun createMediaRecord() {
        /* ①Initial：实例化MediaRecorder对象 */
        mMediaRecorder = MediaRecorder()

        /* setAudioSource/setVedioSource*/
        mMediaRecorder!!.setAudioSource(AudioFileFunc.AUDIO_INPUT) //设置麦克风

        /* 设置输出文件的格式：THREE_GPP/MPEG-4/RAW_AMR/Default
         * THREE_GPP(3gp格式，H263视频/ARM音频编码)、MPEG-4、RAW_AMR(只支持音频且音频编码要求为AMR_NB)
         */
        mMediaRecorder!!.setOutputFormat(MediaRecorder.OutputFormat.DEFAULT)

        /* 设置音频文件的编码：AAC/AMR_NB/AMR_MB/Default */
        mMediaRecorder!!.setAudioEncoder(
            MediaRecorder.AudioEncoder.DEFAULT
        )

        /* 设置输出文件的路径 */
        val file = File(amrFilePath)
        if (file.exists()) {
            file.delete()
        }
        mMediaRecorder!!.setOutputFile(amrFilePath)
    }

    private fun close() {
        if (mMediaRecorder != null) {
            println("stopRecord")
            isRecord = false
            mMediaRecorder!!.stop()
            mMediaRecorder!!.release()
            mMediaRecorder = null
        }
    }

}