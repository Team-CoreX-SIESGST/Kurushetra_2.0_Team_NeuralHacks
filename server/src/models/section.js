// models/section.js
import mongoose from "mongoose";

const sectionSchema = new mongoose.Schema(
    {
        title: {
            type: String,
            required: true,
            trim: true,
            default: "New Chat"
        },
        user: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "User",
            required: true
        }
        // You can add more fields like category, tags, etc. as needed
    },
    { timestamps: true }
);

export default mongoose.model("Section", sectionSchema);
