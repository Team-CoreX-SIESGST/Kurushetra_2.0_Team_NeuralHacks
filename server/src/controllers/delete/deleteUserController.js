import user from '../../models/user.js';
import chat from '../../models/chat.js';
import tokenUsage from '../../models/tokenUsage.js';
import subscription from '../../models/subscription.js';
import { ApiResponse } from '../../utils/apiResponse.js';
import { asyncHandler } from '../../utils/asyncHandler.js';

const deleteUserData = asyncHandler(async (req, res) => {
    const userId = req.user._id; // Assuming you have authentication middleware
    
    // Verify user is deleting their own account
    if (userId.toString() !== req.user._id.toString()) {
        return res.status(403).json(
            new ApiResponse(403, null, "You can only delete your own account")
        );
    }
    
    const session = await mongoose.startSession();
    session.startTransaction();
    
    try {
        // Delete all related data
        await Chat.deleteMany({ user: userId }).session(session);
        await Document.deleteMany({ user: userId }).session(session);
        await TokenUsage.deleteMany({ user: userId }).session(session);
        await Subscription.deleteMany({ user: userId }).session(session);
        
        // Delete the user
        await User.findByIdAndDelete(userId).session(session);
        
        await session.commitTransaction();
        session.endSession();
        
        // Clear authentication cookie/token if needed
        res.clearCookie('accessToken');
        res.clearCookie('refreshToken');
        
        return res.status(200).json(
            new ApiResponse(200, null, "User data deleted successfully")
        );
        
    } catch (error) {
        await session.abortTransaction();
        session.endSession();
        
        console.error('Error deleting user data:', error);
        return res.status(500).json(
            new ApiResponse(500, null, "Error deleting user data")
        );
    }
});

export { deleteUserData };