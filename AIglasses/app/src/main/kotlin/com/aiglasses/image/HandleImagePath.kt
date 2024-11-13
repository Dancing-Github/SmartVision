package com.aiglasses.image

import android.annotation.SuppressLint
import android.content.ContentUris
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.DocumentsContract
import android.provider.MediaStore
import androidx.core.content.FileProvider
import java.io.File

object HandleImagePath {
    fun getRealPath(context: Context, data: Intent): String? {
        // 判断手机系统版本号
        return handleImageOnKitKat(context, data)
    }

    private fun handleImageOnKitKat(context: Context, data: Intent): String? {
        var imagePath: String? = null
        val uri = data.data
        if (DocumentsContract.isDocumentUri(context, uri)) {
            // 如果是document类型的Uri，则通过document id处理
            val docId = DocumentsContract.getDocumentId(uri)
            if ("com.android.providers.media.documents" == uri!!.authority) {
                val id = docId.split(":".toRegex()).dropLastWhile { it.isEmpty() }
                    .toTypedArray()[1] // 解析出数字格式的id
                val selection = MediaStore.Images.Media._ID + "=" + id
                imagePath =
                    getImagePath(context, MediaStore.Images.Media.EXTERNAL_CONTENT_URI, selection)
            } else if ("com.android.providers.downloads.documents" == uri.authority) {
                val contentUri = ContentUris.withAppendedId(
                    Uri.parse("content://downloads/public downloads"),
                    java.lang.Long.valueOf(docId)
                )
                imagePath = getImagePath(context, contentUri, null)
            }
        } else if ("content".equals(uri!!.scheme, ignoreCase = true)) {
            // 如果是content类型的Uri，则使用普通方式处理
            imagePath = getImagePath(context, uri, null)
        } else if ("file".equals(uri.scheme, ignoreCase = true)) {
            // 如果是file类型的Uri，直接获取图片路径即可
            imagePath = uri.path
        }
        //displayImage(imagePath); // 根据图片路径显示图片
        return imagePath
    }

    @SuppressLint("Range")
    private fun getImagePath(context: Context, uri: Uri?, selection: String?): String? {
        var path: String? = null
        // 通过Uri和selection来获取真实的图片路径
        val cursor = context.contentResolver.query(uri!!, null, selection, null, null)
        if (cursor != null) {
            if (cursor.moveToFirst()) {
                path = cursor.getString(cursor.getColumnIndex(MediaStore.Images.Media.DATA))
            }
            cursor.close()
        }
        return path
    }

    private fun getImageUri(context: Context, img: File): Uri {
        return FileProvider.getUriForFile(
            context, "com.aiglasses.fileprovider",//定义唯一标识，关联后面的内容提供器
            img
        )

    }
}
