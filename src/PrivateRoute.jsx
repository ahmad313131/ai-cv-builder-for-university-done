// src/PrivateRoute.jsx
import { Navigate, useLocation } from "react-router-dom";
import { getToken } from "./api";

export default function PrivateRoute({ children }) {
  const token = getToken();
  const location = useLocation();
  if (!token) {
    // بيرجع للمستخدم لنفس الصفحة بعد تسجيل الدخول
    const next = encodeURIComponent(location.pathname + location.search);
    return <Navigate to={`/login?next=${next}`} replace />;
  }
  return children;
}
