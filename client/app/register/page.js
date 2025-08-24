"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Eye,
  EyeOff,
  Mail,
  Lock,
  User,
  Calendar,
  ArrowRight,
  Sparkles,
  AlertCircle,
} from "lucide-react";
import { registerUser } from "@/services/auth/authServices";
import { useGoogleLogin } from "@react-oauth/google";
import { Navbar } from "@/components/layout/Navbar";

// Animation variants for consistency
const FADE_IN_STAGGER_VARIANTS = {
  hidden: { opacity: 0, y: 20 },
  show: {
    opacity: 1,
    y: 0,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const FADE_IN_UP_VARIANTS = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    date_of_birth: "",
    password: "",
    confirmPassword: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isFormValid, setIsFormValid] = useState(false);
  const router = useRouter();

  // Validate form on data change to enable/disable submit button
  useEffect(() => {
    const validate = () => {
      const { name, email, date_of_birth, password, confirmPassword } =
        formData;
      if (!name || !email || !date_of_birth || !password || !confirmPassword)
        return false;
      if (!/\S+@\S+\.\S+/.test(email)) return false;
      if (password.length < 6) return false;
      if (password !== confirmPassword) return false;

      const today = new Date();
      const birthDate = new Date(date_of_birth);
      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (
        monthDiff < 0 ||
        (monthDiff === 0 && today.getDate() < birthDate.getDate())
      ) {
        age--;
      }
      return age >= 13 && birthDate <= today;
    };
    setIsFormValid(validate());
  }, [formData]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError("");
  };

  // Set specific error messages on submit attempt
  const validateOnSubmit = () => {
    if (!formData.name.trim()) {
      setError("Name is required");
      return false;
    }
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setError("Please enter a valid email address");
      return false;
    }
    if (!formData.date_of_birth.trim()) {
      setError("Date of birth is required");
      return false;
    }

    const today = new Date();
    const birthDate = new Date(formData.date_of_birth);
    if (birthDate > today) {
      setError("Date of birth cannot be in the future");
      return false;
    }

    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) age--;
    if (age < 13) {
      setError("You must be at least 13 years old");
      return false;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters");
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateOnSubmit()) return;
    setIsLoading(true);
    setError("");
    try {
      const result = await registerUser(formData);
      if (result?.data) {
        localStorage.setItem("refresh_token", result.data.data.refresh_token);
        localStorage.setItem("user", result.data.data);
      }
      router.push("/");
    } catch (err) {
      setError(err.message || "Registration failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = async (response) => {
    setIsLoading(true);
    setError("");
    try {
      const result = await registerUser({ googleToken: response.access_token });
      if (result?.data) {
        localStorage.setItem("refresh_token", result.data.data.refresh_token);
        localStorage.setItem("user", JSON.stringify(result.data.data));
      }
      router.push("/");
    } catch (err) {
      setError(err.message || "Google registration failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleError = () =>
    setError("Google sign-in failed. Please try again.");

  const googleLogin = useGoogleLogin({
    onSuccess: handleGoogleSuccess,
    onError: handleGoogleError,
    flow: "implicit",
  });

  const today = new Date().toISOString().split("T")[0];
  const minDate = new Date(new Date().getFullYear() - 120, 0, 1)
    .toISOString()
    .split("T")[0];

  return (
    <>
    <div className="relative min-h-screen overflow-hidden bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-4 pt-16">
      <Navbar/>
      <div
        className="absolute inset-0 -z-10 bg-[radial-gradient(45rem_45rem_at_50%_50%,_theme(colors.indigo.100),_transparent_80%)] dark:bg-[radial-gradient(45rem_45rem_at_50%_50%,_theme(colors.indigo.950/40%),_transparent_80%)]"
        aria-hidden="true"
      />

      <motion.div
        initial="hidden"
        animate="show"
        variants={FADE_IN_STAGGER_VARIANTS}
        className="max-w-md w-full space-y-8"
      >
        <motion.div variants={FADE_IN_UP_VARIANTS} className="text-center">
          <div className="inline-flex justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50 mb-2">
            Create an Account
          </h2>
          <p className="text-slate-600 dark:text-slate-400">
            Start your journey with us today.
          </p>
        </motion.div>

        <motion.div
          variants={FADE_IN_UP_VARIANTS}
          className="bg-white/60 dark:bg-slate-900/60 backdrop-blur-lg ring-1 ring-slate-900/10 dark:ring-slate-100/10 rounded-2xl shadow-2xl p-8"
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center space-x-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                <p className="text-red-700 dark:text-red-400 text-sm">
                  {error}
                </p>
              </div>
            )}

            {/* Form Fields */}
            {[
              {
                id: "name",
                name: "name",
                type: "text",
                placeholder: "John Doe",
                icon: User,
                label: "Full Name",
              },
              {
                id: "email",
                name: "email",
                type: "email",
                placeholder: "you@example.com",
                icon: Mail,
                label: "Email Address",
              },
              {
                id: "date_of_birth",
                name: "date_of_birth",
                type: "date",
                placeholder: "",
                icon: Calendar,
                label: "Date of Birth",
              },
              {
                id: "password",
                name: "password",
                type: showPassword ? "text" : "password",
                placeholder: "Min. 6 characters",
                icon: Lock,
                label: "Password",
              },
              {
                id: "confirmPassword",
                name: "confirmPassword",
                type: showConfirmPassword ? "text" : "password",
                placeholder: "Confirm password",
                icon: Lock,
                label: "Confirm Password",
              },
            ].map((field) => (
              <div key={field.id}>
                <label
                  htmlFor={field.id}
                  className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
                >
                  {field.label}
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <field.icon className="h-5 w-5 text-slate-400" />
                  </div>
                  <input
                    id={field.id}
                    name={field.name}
                    type={field.type}
                    required
                    value={formData[field.name]}
                    onChange={handleChange}
                    min={field.type === "date" ? minDate : undefined}
                    max={field.type === "date" ? today : undefined}
                    className="block w-full pl-10 pr-3 py-2.5 bg-slate-50/50 dark:bg-slate-800/40 text-slate-900 dark:text-slate-50 rounded-lg ring-1 ring-inset ring-slate-900/10 dark:ring-slate-100/10 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:ring-2 focus:ring-inset focus:ring-indigo-500 transition-all duration-200"
                    placeholder={field.placeholder}
                  />
                  {(field.name === "password" ||
                    field.name === "confirmPassword") && (
                    <button
                      type="button"
                      onClick={() =>
                        field.name === "password"
                          ? setShowPassword((s) => !s)
                          : setShowConfirmPassword((s) => !s)
                      }
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
                    >
                      {(
                        field.name === "password"
                          ? showPassword
                          : showConfirmPassword
                      ) ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  )}
                </div>
              </div>
            ))}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !isFormValid}
              className="group relative w-full inline-flex items-center justify-center px-6 py-3 mt-4 text-base font-semibold text-white bg-slate-900 rounded-full hover:bg-slate-800 dark:bg-slate-50 dark:text-slate-900 dark:hover:bg-slate-200 transition-all duration-300 shadow-lg disabled:bg-slate-400 dark:disabled:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 mr-2 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                  <span>Creating account...</span>
                </>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight className="w-4 h-4 ml-1.5 group-hover:translate-x-1 transition-transform duration-200" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-300 dark:border-slate-700"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white/0 backdrop-blur-sm text-slate-500 dark:text-slate-400">
                  Or sign up with
                </span>
              </div>
            </div>
          </div>

          {/* Google Button */}
          <div className="mt-6">
            <button
              onClick={() => googleLogin()}
              className="w-full inline-flex justify-center items-center py-2.5 px-4 rounded-lg shadow-sm bg-white dark:bg-slate-800 text-sm font-medium text-slate-600 dark:text-slate-300 ring-1 ring-inset ring-slate-900/10 dark:ring-slate-100/10 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors duration-200"
            >
              <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                {/* Google SVG paths */}
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Sign up with Google
            </button>
          </div>
        </motion.div>

        <motion.div variants={FADE_IN_UP_VARIANTS} className="text-center">
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 transition-colors duration-200"
            >
              Sign in
            </Link>
          </p>
        </motion.div>
      </motion.div>
    </div>
    </>
  );
}
