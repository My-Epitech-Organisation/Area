import { BrowserRouter, Routes, Route } from "react-router-dom";
import Homepage from "./pages/Homepage";
import Navbar from "./components/navbar";

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/Homepage" element={<Homepage />} />
        <Route path="/*" element={<Homepage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
