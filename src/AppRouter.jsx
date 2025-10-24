// src/AppRouter.jsx
import { BrowserRouter, Routes, Route, Navigate , useLocation  } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import App from "./App";
import AppLayout from "./components/AppLayout";
import { getToken } from "./api";
import MyCVs from "./pages/MyCVs";

function PrivateRoute({ children }) {
  const t = getToken(); const loc = useLocation();
  return t ? children : <Navigate to={`/login?next=${encodeURIComponent(loc.pathname)}`} replace />;
}
function PublicOnlyRoute({ children }) {
  const token = getToken();
  return token ? <Navigate to="/builder" replace /> : children;
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* كل الصفحات داخل Layout فيه Header + UserMenu */}
        <Route element={<AppLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/builder" element={<App />} />
          <Route path="/cvs" element={<PrivateRoute><MyCVs /></PrivateRoute>} />
        </Route>

        <Route
          path="/login"
          element={
            <PublicOnlyRoute>
              <Login />
            </PublicOnlyRoute>
          }
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
