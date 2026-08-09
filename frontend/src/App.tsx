import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Landing } from "@/pages/Landing";
import { Login } from "@/pages/Login";
import { Workbench } from "@/pages/Workbench";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/workbench" element={<Workbench />} />
      </Routes>
    </BrowserRouter>
  );
}
