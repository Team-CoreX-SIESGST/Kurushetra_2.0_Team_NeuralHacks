import mongoose from "mongoose";

const planSchema = new mongoose.Schema(
    {
        name: {
            type: String,
            required: true,
            enum: ["Free", "Pro", "Enterprise"]
        },
        price: {
            type: Number,
            required: true,
            default: 0
        },
        tokenLimit: {
            type: Number,
            required: true
        },
        isActive: {
            type: Boolean,
            default: true
        }
    },
    { timestamps: true }
);

export default mongoose.model("Plan", planSchema);
