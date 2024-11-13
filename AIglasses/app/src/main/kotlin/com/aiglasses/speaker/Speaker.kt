package com.aiglasses.speaker

import android.content.Context
import android.speech.tts.TextToSpeech
import android.util.Log
import com.aiglasses.ShowMessageUtil
import com.aiglasses.amap.Navigate
import com.aiglasses.network.HttpUtil
import com.amap.api.navi.AMapNavi
import com.amap.api.navi.model.NaviLatLng
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import org.json.JSONArray
import org.json.JSONObject
import java.util.Locale
import kotlin.coroutines.cancellation.CancellationException


object Speaker {

    private const val RETRIVE_TEXT_GAP: Long = 1000 // ms

    private val texts = Channel<JSONArray>()
    private lateinit var messageCoroutine: MessageCoroutine
    private lateinit var speakCoroutine: SpeakCoroutine
    private lateinit var mainScope: CoroutineScope
    private lateinit var myTTS: MyTextToSpeech


    fun initSpeaker(scope: CoroutineScope) {
        mainScope = scope
        myTTS = MyTextToSpeech(ShowMessageUtil.getAppContext())
//        ShowMessageUtil.showMessage("喇叭启动!")
        messageCoroutine = MessageCoroutine()
        speakCoroutine = SpeakCoroutine()
        messageCoroutine.startThread()
        speakCoroutine.startThread()
    }

    suspend fun addText(arr: JSONArray) {
        texts.send(arr)
    }

    private suspend fun popText(): String {
        val arr = texts.receive()
//      arr= [{"role":"function","name":"depth_estimation","content":"['右前方近处有一个障碍物']"}]
        val tmp = arr[arr.length() - 1]

//        arr = [
//            {
//                "role": "function",
//                "name": "depth_estimation",
//                "content": "测试测试",  # 处理好这个text，然后再传给 android
//                # "content": '{"temperature": "12", "unit": "celsius", "description": "Sunny"}',
//            },
//            {
//                "role": "function",
//                "name": "none",
//                "content": "从前，在一个遥远的国度里，有一位年轻的国王。他名叫亚历山大，是一位非常明智和仁慈的统治者。这个国家的人民都非常尊敬他，并且他的决策总是为国家的利益着想",
//                # "content": '{"temperature": "12", "unit": "celsius", "description": "Sunny"}',
//            }
//        ]

        val json = JSONObject(tmp.toString())
        val str = json["content"]

//        解析一下导航的指令，直接开始导航，不用return文字
        if ((json["role"] == "function" || json["role"] == "tool")
            && json["name"] == "walking_from_org_to_dst"
        ) {
            try {
                val loc = str.toString().split(",")
                //  传过来的经纬度反了 !!!
                val dstPoint = NaviLatLng(loc[1].strip().toDouble(), loc[0].strip().toDouble())
                Log.i("Speaker", dstPoint.toString())
                Navigate.tryNavi(dstPoint)
                ShowMessageUtil.showMessage("尝试计算路径")
            } catch (e: Exception) {
                Log.e("Speaker", e.message!!)
                return "抱歉，找不到相应地点"
            }
            return "尝试计算路径"
        } else if (json["role"] == "function" && json["name"] == "stop_navigate") {
            AMapNavi.getInstance(ShowMessageUtil.getAppContext()).stopNavi()
            ShowMessageUtil.showMessage("导航停止")
            return "导航停止"
        }

        return str.toString()
    }

    internal open class MyCoroutine {
        var vRun = false

        fun stopThread() {
            vRun = false
        }

        fun startThread() {
            if (!vRun) {
                vRun = true
                mainScope.launch { run() }
            }
        }

        open suspend fun run() {
            throw NotImplementedError("Do please override run()")
        }
    }

    internal class SpeakCoroutine : MyCoroutine() {
        override suspend fun run() {
            while (vRun) {
                try {
                    val text = popText()
                    myTTS.speak(text)
                } catch (e: CancellationException) {
                    stopThread()
                    Log.w("TTS", "Speak协程退出$e")
                    break
                } catch (e: Exception) {
                    e.printStackTrace()
                    Log.e("TTS", e.toString())
                }
            }
        }
    }

    internal class MessageCoroutine : MyCoroutine() {
        override suspend fun run() {
            while (vRun) {
                try {
                    delay(RETRIVE_TEXT_GAP)
                    HttpUtil.retrieveText(
                        "${HttpUtil.GLOBAL_URL_TEST}/retrieveText",
                        mainScope
                    )  //检查端口是否可连接
                } catch (e: CancellationException) {
                    stopThread()
                    Log.w("TTS", "Message协程退出$e")
                    break
                } catch (e: Exception) {
                    e.printStackTrace()
                    Log.e("TTS", e.toString())
                }
            }
        }
    }

    internal class MyTextToSpeech(context: Context) : TextToSpeech.OnInitListener {

        private var tts = TextToSpeech(context, this) //初始化失败？

        override fun onInit(status: Int) {
            if (status == TextToSpeech.SUCCESS) {
                Log.i("TTS", "初始化成功")

                // 设置语言
                val result = tts.setLanguage(Locale.CHINA)

                if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    Log.e("TTS", "该语言不支持")
                }

                tts.setSpeechRate(1.5F)
                tts.setPitch(1F)

            } else {
                ShowMessageUtil.showMessage("TTS初始化失败")
                Log.e("TTS", "初始化失败")
            }

        }

        fun speak(text: String) {
            tts.speak(text, TextToSpeech.QUEUE_ADD, null)
            Log.i("TTS", text)
        }

    }
}
