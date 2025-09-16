import React, { useState } from 'react';
import './App.css';

function App() {
  const [response, setResponse] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [city, setCity] = useState('Paris');

  const handleButtonClick = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/trigger', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      setResponse(data.message);
    } catch (error) {
      console.error('Erreur lors de la requête:', error);
      setResponse('Erreur de connexion au serveur');
    }
  };

  const handleWeatherButtonClick = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8080/api/weather?city=${city}`);

      if (!response.ok) {
        throw new Error(`Erreur: ${response.status}`);
      }

      const data = await response.json();
      setWeatherData(data);
    } catch (error) {
      console.error('Erreur lors de la récupération des données météo:', error);
      setWeatherData({ error: 'Impossible de récupérer les données météo' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      <div className="w-full max-w-md p-8 mx-auto bg-white bg-opacity-90 backdrop-blur-sm rounded-xl shadow-2xl border border-white border-opacity-20">
        <h1 className="text-3xl font-bold text-indigo-600 mb-8 text-center">
          POC Action-Réaction
        </h1>
        <button
          onClick={handleButtonClick}
          className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition duration-300 ease-in-out transform hover:scale-105 mb-4"
        >
          Déclencher une action
        </button>
        {response && (
          <div className="mt-2 mb-4 p-4 bg-green-100 text-green-800 rounded-md">
            {response}
          </div>
        )}
        <div className="mt-4 mb-4">
          <div className="flex items-center mb-2">
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="Entrez une ville"
              className="flex-1 p-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-yellow-400"
            />
          </div>
          <button
            onClick={handleWeatherButtonClick}
            disabled={loading}
            className="w-full flex items-center justify-center bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition duration-300 ease-in-out transform hover:scale-105"
          >
            <span className="mr-2 text-2xl">☀️</span>
            {loading ? 'Chargement...' : 'Météo'}
          </button>
        </div>
        {weatherData && !weatherData.error && (
          <div className="mt-4 p-4 bg-blue-50 text-blue-800 rounded-md">
            <div className="flex items-center mb-2">
              <img
                src={`http://openweathermap.org/img/wn/${weatherData.icon}@2x.png`}
                alt={weatherData.description}
                className="w-16 h-16 mr-2"
              />
              <div>
                <h3 className="text-xl font-bold">{weatherData.city}</h3>
                <p className="capitalize">{weatherData.description}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <div className="p-2 bg-white rounded-md">
                <p className="text-sm text-gray-500">Température</p>
                <p className="text-lg font-bold">{weatherData.temperature}°C</p>
              </div>
              <div className="p-2 bg-white rounded-md">
                <p className="text-sm text-gray-500">Ressenti</p>
                <p className="text-lg font-bold">{weatherData.feelsLike}°C</p>
              </div>
              <div className="p-2 bg-white rounded-md">
                <p className="text-sm text-gray-500">Humidité</p>
                <p className="text-lg font-bold">{weatherData.humidity}%</p>
              </div>
              <div className="p-2 bg-white rounded-md">
                <p className="text-sm text-gray-500">Vent</p>
                <p className="text-lg font-bold">{weatherData.windSpeed} m/s</p>
              </div>
            </div>
          </div>
        )}
        {weatherData && weatherData.error && (
          <div className="mt-4 p-4 bg-red-100 text-red-800 rounded-md">
            {weatherData.error}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
