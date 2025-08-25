import mongoose from 'mongoose';
import connectDB from '../db/index.js';
import User from '../models/user.js';
import Chat from '../models/chat.js';
import Document from '../models/document.js';
import TokenUsage from '../models/tokenUsage.js';
import Subscription from '../models/subscription.js';
import Plan from '../models/plan.js';
import Section from '../models/section.js';

// Connect to database
connectDB();

const deleteUserData = async (userId) => {
    try {
        console.log(`Starting deletion process for user: ${userId}`);
        
        // If you want to delete all users, use this instead:
        // const allUsers = await User.find({});
        // for (const user of allUsers) {
        //   await deleteSingleUserData(user._id);
        // }
        
        await deleteSingleUserData(userId);
        
        console.log('User data deletion completed successfully');
        process.exit(0);
    } catch (error) {
        console.error('Error deleting user data:', error);
        process.exit(1);
    }
};

const deleteSingleUserData = async (userId) => {
    const session = await mongoose.startSession();
    session.startTransaction();
    
    try {
        // Delete related data first (maintain referential integrity)
        await Chat.deleteMany({ user: userId }).session(session);
        await Document.deleteMany({ user: userId }).session(session);
        await TokenUsage.deleteMany({ user: userId }).session(session);
        await Subscription.deleteMany({ user: userId }).session(session);
        
        // If sections are user-specific, delete them too
        // await Section.deleteMany({ user: userId }).session(session);
        
        // Finally delete the user
        const result = await User.findByIdAndDelete(userId).session(session);
        
        await session.commitTransaction();
        session.endSession();
        
        console.log(`Deleted user: ${userId}, Result:`, result);
        return result;
    } catch (error) {
        await session.abortTransaction();
        session.endSession();
        throw error;
    }
};

// Get user ID from command line arguments or set manually
const userId = process.argv[2] || 'SPECIFIC_USER_ID_HERE';

if (!userId || userId === 'SPECIFIC_USER_ID_HERE') {
    console.error('Please provide a user ID as argument: npm run delete-user -- USER_ID_HERE');
    process.exit(1);
}

deleteUserData(userId);