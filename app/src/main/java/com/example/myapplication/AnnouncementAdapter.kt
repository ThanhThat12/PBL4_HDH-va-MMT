import com.example.myapplication.Announcement // Thay thế bằng package thực tế của bạn
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.myapplication.R
import android.text.method.LinkMovementMethod
import android.text.util.Linkify

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

        // Làm các liên kết có thể nhấp
        holder.contentTextView.autoLinkMask = Linkify.WEB_URLS
        holder.contentTextView.movementMethod = LinkMovementMethod.getInstance()

    }

    override fun getItemCount() = announcements.size
}
