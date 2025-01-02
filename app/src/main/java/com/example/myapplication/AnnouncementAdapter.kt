import android.content.Intent
import android.net.Uri
import android.text.Spannable
import android.text.SpannableStringBuilder
import android.text.method.LinkMovementMethod
import android.text.style.ClickableSpan
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.myapplication.Announcement // Thay thế bằng package thực tế của bạn
import com.example.myapplication.R

class AnnouncementAdapter(private val announcements: List<Announcement>) : RecyclerView.Adapter<AnnouncementAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val contentTextView: TextView = view.findViewById(R.id.contentTextView)
        val dateTextView: TextView = view.findViewById(R.id.dateTextView)
        val titleTextView: TextView = view.findViewById(R.id.titleTextView)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.announcement_item, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val announcement = announcements[position]
        holder.contentTextView.text = announcement.content
        holder.dateTextView.text = announcement.date
        holder.titleTextView.text = announcement.title

        // Lấy nội dung của thông báo và thay thế tất cả các URL bằng chữ "tại đây"
        val urlRegex = "(https?://\\S+)".toRegex() // Biểu thức chính quy để tìm tất cả các URL
        val content = announcement.content.replace(Regex("[()]"), "") // Loại bỏ dấu ngoặc ( và )
        val spannableStringBuilder = SpannableStringBuilder(content)

        // Duyệt qua tất cả các URL trong chuỗi
        val matches = urlRegex.findAll(content)
        var offset = 0 // Dùng để điều chỉnh vị trí sau mỗi lần thay thế URL bằng "tại đây"

        matches.forEach { match ->
            val url = match.value // Lấy URL từ nội dung
            val start = match.range.first - offset // Tính toán vị trí bắt đầu sau khi thay thế
            val end = match.range.last + 1 - offset // Tính toán vị trí kết thúc sau khi thay thế

            // Thay thế URL bằng "tại đây"
            spannableStringBuilder.replace(start, end, "tại đây")
            offset += url.length - "tại đây".length

            // Gán sự kiện nhấp vào cho phần "tại đây"
            val clickableSpan = object : ClickableSpan() {
                override fun onClick(widget: View) {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url)) // Mở URL trong trình duyệt
                    widget.context.startActivity(intent)
                }
            }

            // Áp dụng sự kiện nhấp vào chữ "tại đây"
            spannableStringBuilder.setSpan(clickableSpan, start, start + "tại đây".length, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE)
        }

        holder.contentTextView.text = spannableStringBuilder
        holder.contentTextView.movementMethod = LinkMovementMethod.getInstance() // Cho phép nhấp vào liên kết

    }

    override fun getItemCount() = announcements.size

}
