// scripts/seedPlans.js
import mongoose from "mongoose";
import Plan from "../models/plan.js";
import dotenv from "dotenv";

dotenv.config();

const plans = [
    {
        name: "Free",
        price: 0,
        tokenLimit: 1000000 // 10 lakh tokens
    },
    {
        name: "Pro",
        price: 899,
        tokenLimit: 20000000 // 2 crore tokens
    },
    {
        name: "Enterprise",
        price: 4899,
        tokenLimit: -1 // Unlimited
    }
];

const seedPlans = async () => {
    try {
        await mongoose.connect(process.env.MONGODB_URI);

        for (let plan of plans) {
            await Plan.findOneAndUpdate({ name: plan.name }, plan, { upsert: true, new: true });
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
