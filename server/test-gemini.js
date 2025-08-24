// test-gemini.js
import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI("AIzaSyBYNbOUVDz92M14KHU9vJ-rBKrQtz7hNZ8");

async function testGemini() {
    try {
        // Use the correct model name - gemini-pro is now called gemini-1.0-pro
        const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

        const result = await model.generateContent("Hello, how are you?");
        const response = await result.response;
        const text = response.text();
        console.log("Gemini response:", text);
    } catch (error) {
        console.error("Error testing Gemini:", error);

        // Try with the flash model if pro fails
        try {
            console.log("Trying with gemini-1.0-flash model...");
            const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

            const result = await model.generateContent("Hello, how are you?");
            const response = await result.response;
            const text = response.text();
            console.log("Gemini flash response:", text);
        } catch (flashError) {
            console.error("Error with flash model too:", flashError);
        }
    }
}

testGemini();
