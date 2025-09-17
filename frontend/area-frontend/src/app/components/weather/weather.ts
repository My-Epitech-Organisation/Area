import { Component, signal } from '@angular/core';
import { NgIf } from '@angular/common';
import { Api } from '../../services/api';
import { WeatherData } from '../../models/api.models';

@Component({
  selector: 'app-weather',
  imports: [NgIf],
  templateUrl: './weather.html',
  styleUrl: './weather.scss'
})
export class Weather {
  protected city = signal<string>('Paris');
  protected weatherData = signal<WeatherData | null>(null);
  protected loading = signal<boolean>(false);
  protected error = signal<string | null>(null);

  constructor(private apiService: Api) {
    this.getWeather(this.city());
  }

  getWeather(city: string) {
    if (!city.trim()) {
      this.error.set('Veuillez entrer un nom de ville');
      return;
    }

    this.city.set(city);
    this.loading.set(true);
    this.error.set(null);

    this.apiService.getWeather(city).subscribe({
      next: (data) => {
        this.weatherData.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Erreur lors de la récupération des données météo:', err);
        this.error.set('Erreur lors de la récupération des données météo. Veuillez réessayer.');
        this.loading.set(false);
      }
    });
  }
}
