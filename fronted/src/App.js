import Login from "./pages/Login";
import Profile from "./pages/Profile";


function App() {
  const path = window.location.pathname;

  if (path === "/profile") {
    return <Profile />;
  }

  return <Login />;
}

export default App;

