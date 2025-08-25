import mongoose from "mongoose";

const userSchema = new mongoose.Schema(
    {
        name: {
            type: String,
            required: true,
            trim: true
        },
        email: {
            type: String,
            required: true,
            unique: true,
            trim: true
        },
        password: {
            type: String,
            required: false
        },
        image: {
            type: String,
            default: null
        },
        refresh_token: String,
        token_version: {
            type: Number,
            default: 0
        },
        date_of_birth: {
            type: String,
            default: null
        },
        googleId: {
            type: String,
            unique: true,
            sparse: true
        },
        // New subscription fields
        plan: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "Plan",
            required: true
        },
        tokensUsed: {
            type: Number,
            default: 0
        },
        tokenResetDate: {
            type: Date,
            default: Date.now
        },
        subscriptionStatus: {
            type: String,
            enum: ["active", "canceled", "expired"],
            default: "active"
        },
        subscriptionId: String // For payment gateway reference
    },
    { timestamps: true }
);

export default mongoose.model("User", userSchema);
