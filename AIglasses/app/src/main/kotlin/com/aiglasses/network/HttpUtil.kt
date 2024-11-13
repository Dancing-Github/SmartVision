package com.aiglasses.network

import android.util.Log
import com.aiglasses.image.Camera
import com.aiglasses.speaker.Speaker.addText
import com.amap.api.navi.model.NaviLatLng
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch
import okhttp3.Call
import okhttp3.Callback
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import okhttp3.Response
import okio.Buffer
import org.json.JSONArray
import java.io.File
import java.io.IOException
import java.util.concurrent.TimeUnit

object HttpUtil {

    val GLOBAL_URL_TEST = "http://localhost:28080"
//    val GLOBAL_URL_TEST = "http://10.0.2.2:28080"
//    val GLOBAL_URL_TEST = "http://192.168.88.100:28080"

    //发送请求
    private val client = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS) //设置连接超时时间
        .readTimeout(5, TimeUnit.SECONDS) //设置读取超时时间
        .build()

    private var LOCATION_LAT_LNG = NaviLatLng(23.04367093310192, 113.41183934259199)  //初始在广州大学城

    fun update_device_location(latLng: NaviLatLng) {
        LOCATION_LAT_LNG = latLng
    }

    fun retrieveText(url: String, mainScope: CoroutineScope) {

        //构建request
        val request: Request = Request.Builder()
            .url(url)
            .addHeader("LAT",LOCATION_LAT_LNG.latitude.toString())
            .addHeader("LNG",LOCATION_LAT_LNG.longitude.toString())
            .build()

        //调用newCall 返回call对象，此后调用enqueue进行异步请求
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.d("retrieveText", "连接异常，go failure ${e.message}")
//                ShowMessageUtil.showMessage("连接异常")
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    val res = response.body?.string()
                    val txt = res?.let { JSONArray(it) }
                    if (txt != null) {
                        Log.d("Retrieve Text", response.toString())
                        if (txt.length() > 0) {
                            mainScope.launch { addText(txt) }
                        }
                    }
                } else {
                    Log.d("Retrieve Text", "failure ${response.message}")
                }
                response.close()
            }
        })
    }


    /**
     *
     * @param address  服务器地址
     * @param requestBody  请求体数据
     */
    fun uploadFile(
        address: String,
        requestBody: RequestBody,
        tempFileToDelete: File? = null
    ) {

        val request: Request = Request.Builder()
            .url(address)
            .post(requestBody)
            .build()

        // 打印请求信息
        Log.d("HttpUtil", "Request URL: $address")
        Log.d("HttpUtil", "Request Headers: " + request.headers)
        client.newCall(request).enqueue(object : Callback {
            //请求失败回调函数
            override fun onFailure(call: Call, e: IOException) {
                if (tempFileToDelete != null) {
                    Camera.deleteTempFile(tempFileToDelete)
                }
                Log.e("uploadFile", "上传异常 ${e.message}")
//                ShowMessageUtil.showMessage("上传异常")
            }

            //请求成功响应函数
            override fun onResponse(call: Call, response: Response) {
                if (tempFileToDelete != null) {
                    Camera.deleteTempFile(tempFileToDelete)
                }

                val msg = if (response.isSuccessful) {
                    "success ${response.message}"
                } else {
                    "failure ${response.message}"
                }
                Log.d(
                    "uploadFile",
                    "Response: ${msg} RequestBody.contentLength :${requestBody.contentLength()}"
                )
                response.close()
            }
        })
    }

    private fun requestBodyToString(requestBody: RequestBody): String {
        try {
            val buffer = Buffer()
            requestBody.writeTo(buffer)
            return buffer.readUtf8()
        } catch (e: IOException) {
            e.printStackTrace()
        }
        return ""
    }


}
