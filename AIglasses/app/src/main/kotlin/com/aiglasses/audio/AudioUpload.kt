package com.aiglasses.audio

import com.aiglasses.ShowMessageUtil
import com.aiglasses.network.HttpUtil
import com.aiglasses.network.HttpUtil.GLOBAL_URL_TEST
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.IOException


object AudioUpload {
    private const val MIN_AUDIO_SIZE = 2000//bytes

    //上传图片
    fun uploadAudio(audioFilePath: String) {

        val audioFile = try {
            File(audioFilePath)
        } catch (e: IOException) {
            e.printStackTrace()
            null
        }


        if (audioFile == null || audioFile.length() < MIN_AUDIO_SIZE) {
            ShowMessageUtil.showMessage("空录音文件")
//            if (Looper.myLooper() == null) {
//                Looper.prepare()
//            }
//            Toast.makeText(context, "空录音文件", Toast.LENGTH_SHORT).show()
            return
        }


        val requestBody: RequestBody =
            audioFile.asRequestBody("text/x-markdown; charset=utf-8".toMediaType()).let {
                MultipartBody.Builder()
                    .setType(MultipartBody.FORM)
                    .addFormDataPart(
                        "audioFile",
                        audioFile.name,
                        it
                    )
                    .build()
            }

        ShowMessageUtil.showMessage(audioFile.name)
//        if (Looper.myLooper() == null) {
//            Looper.prepare()
//        }
//        Toast.makeText(context, audioFile.name, Toast.LENGTH_SHORT).show()

        //调用HttpUtil工具类上传图片以及参数
        HttpUtil.uploadFile(
            "${GLOBAL_URL_TEST}/uploadAudio",
            requestBody,
        )
    }
}