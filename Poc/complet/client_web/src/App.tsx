/*
** EPITECH PROJECT, 2025
** Area
** File description:
** App
*/

import { useEffect, useState } from "react";

function App() {
  const [about, setAbout] = useState<any>(null);

  useEffect(() => {
    fetch("http://server:8080/about.json")
      .then(res => res.json())
      .then(setAbout);
  }, []);

  return (
    <div>
      <h1>AREA Client Web</h1>
      {about ? <pre>{JSON.stringify(about, null, 2)}</pre> : "Loading..."}
      <a href="/apks/client.apk" download>Download Mobile APK</a>
    </div>
  );
}
export default App;
