package com.aiglasses.amap

import android.content.Context
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.aiglasses.R
import com.amap.api.services.help.Tip

class RvAdapter(
    private val list: ArrayList<Tip>,
    private val context: Context,
    private val rv: RecyclerView
) : RecyclerView.Adapter<RvAdapter.ViewHolder>(), View.OnClickListener {
    private var mOnItemClickListener: OnItemClickListener? = null
    override fun onClick(view: View) {
        val position = rv.getChildAdapterPosition(view)

        //程序执行到此，会去执行具体实现的onItemClick()方法
        if (mOnItemClickListener != null) {
            mOnItemClickListener!!.onItemClick(rv, view, position, list[position])
        }
    }

    interface OnItemClickListener {
        fun onItemClick(recyclerView: RecyclerView?, view: View?, position: Int, data: Tip?)
    }

    fun setmOnItemClickListener(clickListener: OnItemClickListener?) {
        mOnItemClickListener = clickListener
    }

    fun setData(list1: List<Tip>?) {
        if (list1 != null) {
            list.clear()
            list.addAll(list1)
            notifyDataSetChanged()
        }
    }

    fun clearData() {
        list.clear()
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = View.inflate(context, R.layout.item, null)
        view.setOnClickListener(this)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val tip = list[position]
        holder.textView.text = tip.name
    }

    override fun getItemCount(): Int {
        return list.size
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val textView: TextView

        init {
            textView = itemView.findViewById(R.id.search_adapter_text)
        }
    }
}
