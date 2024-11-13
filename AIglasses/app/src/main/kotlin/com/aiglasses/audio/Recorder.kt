package com.aiglasses.audio

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.Message
import android.util.Log
import com.aiglasses.ShowMessageUtil
import com.aiglasses.audio.AudioUpload.uploadAudio
import kotlin.math.log10


object Recorder {
    private var mState = -1 //-1:没再录制，0：录制wav，1：录制amr
    private var uiThread: UIThread? = null
    private var volumeThread: VolumeThread? = null
    private var uiHandler = UIHandler


    const val THRESH_HOLD_DB = 65
    const val MEASURE_SILENCE_MS: Long = 100  // 音量检测采样间隔
    const val DOWN_COUNT_TIME: Long = 100 // 最长10s
    const val DOWN_COUNT_SILENCE = 20  // 最大安静次数
    const val FLAG_WAV = 0
    const val FLAG_AMR = 1
    private const val CMD_RECORDING_TIME = 2000
    private const val CMD_RECORD_FAIL = 2001
    private const val CMD_STOP = 2002


    private fun getVolume(): Int {
        var result = 0
        when (mState) {
            FLAG_WAV -> result = AudioRecordFunc.getVolume() // not implemented
            FLAG_AMR -> result = MediaRecordFunc.getVolume()
        }
        return result
    }


    /**
     * 开始录音
     * @param mFlag，0：录制wav格式，1：录音amr格式
     */
    fun record(mFlag: Int) {
        if (mState != -1) {
            val msg = Message()
            val msgData = Bundle() // 存放数据
            msgData.putInt("cmd", CMD_RECORD_FAIL)
            msgData.putInt("msg", ErrorCode.E_STATE_RECODING)
            msg.data = msgData
            uiHandler.sendMessage(msg) // 向Handler发送消息,更新UI
            return
        }
        var mResult = -1
        when (mFlag) {
            FLAG_WAV -> mResult = AudioRecordFunc.startRecordAndFile()
            FLAG_AMR -> mResult = MediaRecordFunc.startRecordAndFile()
        }
        if (mResult == ErrorCode.SUCCESS) {
            uiThread = UIThread()
            volumeThread = VolumeThread()
            mState = mFlag
            Thread(volumeThread).start()
            Thread(uiThread).start()
        } else {
            val msg = Message()
            val msgData = Bundle() // 存放数据
            msgData.putInt("cmd", CMD_RECORD_FAIL)
            msgData.putInt("msg", mResult)
            msg.data = msgData
            uiHandler.sendMessage(msg) // 向Handler发送消息,更新UI
        }
    }

    /**
     * 停止录音
     */
    fun stop() {
        if (mState != -1) {
            when (mState) {
                FLAG_WAV -> {
                    AudioRecordFunc.stopRecordAndFile()
                    uploadAudio(AudioFileFunc.wavFilePath)
                }

                FLAG_AMR -> {
                    MediaRecordFunc.stopRecordAndFile()
                    uploadAudio(AudioFileFunc.amrFilePath)
                }
            }
            if (uiThread != null) {
                uiThread!!.stopThread()
            }
            if (volumeThread != null) {
                volumeThread!!.stopThread()
            }
            uiHandler.removeCallbacks(uiThread!!)
            uiHandler.removeCallbacks(volumeThread!!)
            val msg = Message()
            val msgData = Bundle() // 存放数据
            msgData.putInt("cmd", CMD_STOP)
            msgData.putInt("msg", mState)
            msg.data = msgData
            uiHandler.sendMessageDelayed(msg, 1000) // 向Handler发送消息,更新UI
            mState = -1
        }
        ShowMessageUtil.startWakeUp()
    }

    //可能有内存泄露
    internal object UIHandler : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            // TODO Auto-generated method stub
            Log.d("MyHandler", "handleMessage......")
            super.handleMessage(msg)
            val msgData = msg.data
            when (msgData.getInt("cmd")) {
                CMD_RECORDING_TIME -> {
                    val vTime = msgData.getInt("msg")
                    ShowMessageUtil.setText("正在录音中，已录制：$vTime s")
                }

                CMD_RECORD_FAIL -> {
                    val vErrorCode = msgData.getInt("msg")
                    val vMsg =
                        ErrorCode.getErrorInfo(ShowMessageUtil.getAppContext(), vErrorCode)
                    ShowMessageUtil.setText("正在录音中，已录制：$vMsg s")
                }

                CMD_STOP -> {
                    val vFileType = msgData.getInt("msg")
                    when (vFileType) {
                        FLAG_WAV -> {
                            val mRecord_1 = AudioRecordFunc

                            val mSize = mRecord_1.recordFileSize
                            ShowMessageUtil.setText(
                                """
                                录音已停止.录音文件:${AudioFileFunc}
                                文件大小：$mSize
                                """.trimIndent()
                            )

                        }

                        FLAG_AMR -> {
                            val mRecord_2 = MediaRecordFunc
                            val mSize = mRecord_2.recordFileSize
                            ShowMessageUtil.setText(
                                """
                                录音已停止.录音文件:${AudioFileFunc}
                                文件大小：$mSize
                                """.trimIndent()
                            )
                        }
                    }

                }

                else -> {}
            }
        }
    }

    internal class VolumeThread : Runnable {
        private var vRun = true
        private var recentVolume = ArrayDeque<Int>()
        fun stopThread() {
            vRun = false
        }

        override fun run() {
            var countTime = DOWN_COUNT_TIME
            var countSilence = DOWN_COUNT_SILENCE
            while (vRun) {
                try {
                    Thread.sleep(MEASURE_SILENCE_MS)
                    --countSilence
                    --countTime
                } catch (e: InterruptedException) {
                    // TODO Auto-generated catch block
                    e.printStackTrace()
                }

                recentVolume.addLast(getVolume())
                //  检测窗口大小为 最大安静次数 的一半
                if (recentVolume.count() > DOWN_COUNT_SILENCE / 2) {
                    recentVolume.removeFirst()
                    val ratio = recentVolume.average()
                    if (ratio > 1) {
                        val db = 20 * log10(ratio)
                        Log.d("thread", "分贝值：$db")
                        if (db >= THRESH_HOLD_DB) {
                            countSilence = DOWN_COUNT_SILENCE
                        }
                    }
                }
                if ((countSilence < 0 || countTime < 0) && vRun) {
                    stop()
                }
                Log.d("thread", "countSilence........$countSilence")
            }

        }
    }


    internal class UIThread : Runnable {
        private var mTimeMill = 0
        private var vRun = true

        fun stopThread() {
            vRun = false
        }

        override fun run() {
            while (vRun) {
                try {
                    Thread.sleep(1000)
                    ++mTimeMill
                } catch (e: InterruptedException) {
                    // TODO Auto-generated catch block
                    e.printStackTrace()
                }

                Log.d("thread", "mThread........$mTimeMill")
                val msg = Message()
                val msgData = Bundle() // 存放数据
                msgData.putInt("cmd", CMD_RECORDING_TIME)
                msgData.putInt("msg", mTimeMill)
                msg.data = msgData
                uiHandler.sendMessage(msg) // 向Handler发送消息,更新UI

                // Inflate the layout for this fragment
            }
        }
    }


}


