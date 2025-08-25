import mongoose from "mongoose";
import Plan from "../models/plan.js";
import dotenv from "dotenv";

dotenv.config();

const plans = [
    {
        name: "Free",
        price: 0,
        tokenLimit: 1000000, // 10 lakh tokens
        popular: false,
        features: [
            "10 lakh tokens per month",
            "Basic chat functionality",
            "Standard response quality",
            "Basic document processing (up to 5 documents)",
            "Limited research capabilities"
        ]
    },
    {
        name: "Pro",
        price: 899,
        tokenLimit: 20000000, // 2 crore tokens
        popular: true,
        features: [
            "2 crore tokens per month",
            "Advanced research capabilities",
            "Enhanced document processing (up to 50 documents)",
            "Google Drive integration",
            "Advanced visualization options",
            "Export research reports",
            "Early access to new features"
        ]
    },
    {
        name: "Enterprise",
        price: 4899,
        tokenLimit: -1, // Unlimited
        popular: false,
        features: [
            "Unlimited tokens",
            "All Pro features",
            "Unlimited document processing",
            "Unlimited team members",
            "API access",
            "Custom integrations",
            "24/7 priority support"
        ]
    }
];

const seedPlans = async () => {
    try {
        await mongoose.connect(
            process.env.MONGODB_URI || "mongodb+srv://suthakar:suthakar123@cluster0.8gdct.mongodb.net/kurukshetra"
        );
        console.log("Connected to MongoDB");

        // Delete existing plans
        await Plan.deleteMany({});
        console.log("Cleared existing plans");

        // Insert new plans
        for (let plan of plans) {
            await Plan.create(plan);
            console.log(`Plan ${plan.name} seeded successfully`);
        }

        console.log("All plans seeded successfully");
        process.exit(0);
    } catch (error) {
        console.error("Error seeding plans:", error);
        process.exit(1);
    }
};

seedPlans();
