package com.aiglasses.image

import android.os.Environment
import android.util.Log
import android.util.Size
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.core.impl.CaptureProcessor
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import com.aiglasses.MainActivity
import com.aiglasses.ShowMessageUtil
import java.io.ByteArrayOutputStream
import java.io.File
import java.util.concurrent.Executors


class Camera(mainAtv: MainActivity) {

    companion object {
        private const val TAKE_PHOTO_GAP: Long = 3000 // ms

        // Function to explicitly delete a file
        fun deleteTempFile(file: File) {
            if (file.delete()) {
                Log.d("take_photo_thread", "Temporary file deleted successfully.")
            } else {
                Log.e("take_photo_thread", "Unable to delete the temporary file.")
            }
        }
    }


    private var uploadThread = UploadThread()
    private var mainActivity = mainAtv
    private var cameraProviderFuture = ProcessCameraProvider.getInstance(mainActivity)
    private var cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
    private var imgCaptureExecutor = Executors.newSingleThreadExecutor()
    private var imageCapture: ImageCapture? = null


    fun stopUpload() {
        uploadThread.stopThread()
    }


    fun startCamera() {
        // listening for data from the camera
        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()

            // connecting a preview use case to the preview in the xml file.
            val preview = Preview.Builder()
                .setTargetResolution(Size(320, 240))
                .build().also {
                it.setSurfaceProvider(mainActivity.getBinding().ivCamera.surfaceProvider)
            }

            imageCapture = ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .setTargetResolution(Size(1600, 1200))
                .build()

            try {
                // clear all the previous use cases first.
                cameraProvider.unbindAll()
                // binding the lifecycle of the camera to the lifecycle of the application.
                cameraProvider.bindToLifecycle(mainActivity, cameraSelector, preview)
                cameraProvider.bindToLifecycle(mainActivity, cameraSelector, preview, imageCapture)
            } catch (e: Exception) {
                Log.d("MainActivity", "Use case binding failed")
            }

        }, ContextCompat.getMainExecutor(mainActivity))

        Thread(uploadThread).start()
//        ShowMessageUtil.showMessage("相机启动！")
    }


    fun takePhoto(): File? {

        val imageDir = File(Environment.getExternalStorageDirectory().absolutePath, "aiglasses")
        if (!imageDir.exists()) {
            imageDir.mkdir()
        }

        imageCapture?.let {

            fun capture_in_memory() {
                val outputStream = ByteArrayOutputStream()
                // Save the image in the buffer
                val outputFileOptions = ImageCapture.OutputFileOptions.Builder(outputStream).build()
                it.takePicture(
                    outputFileOptions,
                    imgCaptureExecutor,
                    object : ImageCapture.OnImageSavedCallback {
                        override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                            Log.i("take_photo_thread", "The image has been saved in memory")
                            ImageUpload.uploadImage(outputStream.toByteArray())
                        }

                        override fun onError(exception: ImageCaptureException) {
                            ShowMessageUtil.showMessage("Error taking photo")
                            Log.d("MainActivity", "Error taking photo:$exception")
                        }
                    }
                )
            }

            fun capture_as_file() {
                val outputImage =
                    File(imageDir, "output_image_" + System.currentTimeMillis() + ".jpg")
                // Save the image in the file
                val outputFileOptions = ImageCapture.OutputFileOptions.Builder(outputImage).build()
                it.takePicture(
                    outputFileOptions,
                    imgCaptureExecutor,
                    object : ImageCapture.OnImageSavedCallback {
                        override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                            Log.i(
                                "take_photo_thread",
                                "The image has been saved in ${outputFileResults.savedUri}"
                            )
                            ImageUpload.uploadImage(outputImage)
                        }

                        override fun onError(exception: ImageCaptureException) {
                            ShowMessageUtil.showMessage("Error taking photo")
                            Log.d("MainActivity", "Error taking photo:$exception")
                            deleteTempFile(outputImage)
                        }
                    }
                )
            }

//            capture_in_memory()
            capture_as_file()
        }
        return null
    }

    internal inner class UploadThread : Runnable {
        private var vRun = true

        fun stopThread() {
            vRun = false
        }

        override fun run() {

            while (vRun) {
                try {
                    Thread.sleep(TAKE_PHOTO_GAP)
                    Log.d("take_photo_thread", "takePhoto before..")
                    takePhoto()
                } catch (e: Exception) {
                    e.printStackTrace()
                    Log.e("take_photo_thread", "takePhoto fail....$e")
                }
            }
        }
    }


}