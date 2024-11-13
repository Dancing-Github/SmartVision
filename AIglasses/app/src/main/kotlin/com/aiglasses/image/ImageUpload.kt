package com.aiglasses.image

import com.aiglasses.ShowMessageUtil
import com.aiglasses.network.HttpUtil
import com.aiglasses.network.HttpUtil.GLOBAL_URL_TEST
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File


object ImageUpload {

    private const val MIN_IMAGE_SIZE = 25000//bytes

    //上传图片
    fun uploadImage(imgFile: File?) {

        if (imgFile == null || imgFile.length() < MIN_IMAGE_SIZE) {
            ShowMessageUtil.showMessage("错误图片")
            if (imgFile != null) {
                Camera.deleteTempFile(imgFile)
            }
            return
        }
        val requestBody =
            imgFile.asRequestBody("image/jpeg".toMediaType()).let {
                MultipartBody.Builder().setType(MultipartBody.FORM)
                    .addFormDataPart(
                        "imageFile",
                        imgFile.name,
                        it
                    ).build()
            }

        //调用HttpUtil工具类上传图片以及参数
        HttpUtil.uploadFile(
            "${GLOBAL_URL_TEST}/uploadImage",
            requestBody, imgFile
        )
    }

    fun uploadImage(imageBytes: ByteArray) {

        if (imageBytes.size < MIN_IMAGE_SIZE) {
            ShowMessageUtil.showMessage("错误图片")
            return
        }
        // Create a request body with the image and the media type
        val requestBody =
            imageBytes.toRequestBody("image/jpeg".toMediaType(), 0, imageBytes.size).let {
                MultipartBody.Builder().setType(MultipartBody.FORM)
                    .addFormDataPart(
                        "imageFile",
                        "output_image.jpg",
                        it
                    ).build()
            }

        //调用HttpUtil工具类上传图片以及参数
        HttpUtil.uploadFile(
            "${GLOBAL_URL_TEST}/uploadImage",
            requestBody,
        )
    }
}