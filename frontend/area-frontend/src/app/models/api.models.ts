export interface User {
  id?: number;
  username: string;
  email: string;
  role: string;
}

export interface WeatherData {
  city: string;
  temperature: string;
  feelsLike: string;
  humidity: number;
  windSpeed: string;
  description: string;
  icon: string;
}

export interface TranslationRequest {
  text: string;
  targetLang: string;
}

export interface TranslationResponse {
  originalText: string;
  translatedText: string;
  targetLang: string;
  sourceLang: string;
}
