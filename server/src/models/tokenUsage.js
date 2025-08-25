import mongoose from "mongoose";

const tokenUsageSchema = new mongoose.Schema(
    {
        user: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "User",
            required: true
        },
        tokens: {
            type: Number,
            required: true
        },
        message: {
            type: String,
            required: true
        },
        isUserMessage: {
            type: Boolean,
            default: true
        },
        section: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Section"
        }
    },
    { timestamps: true }
);

export default mongoose.model("TokenUsage", tokenUsageSchema);
