import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { User, WeatherData, TranslationRequest, TranslationResponse } from '../models/api.models';

@Injectable({
  providedIn: 'root'
})
export class Api {
  private apiUrl = 'http://localhost:8081/api';

  constructor(private http: HttpClient) { }

  getHealthStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`);
  }

  triggerAction(): Observable<any> {
    return this.http.post(`${this.apiUrl}/trigger`, {});
  }

  getWeather(city: string = 'Paris'): Observable<WeatherData> {
    return this.http.get<WeatherData>(`${this.apiUrl}/weather`, {
      params: { city }
    });
  }

  translateText(request: TranslationRequest): Observable<TranslationResponse> {
    return this.http.post<TranslationResponse>(`${this.apiUrl}/translate`, request);
  }

  getAllUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.apiUrl}/users`);
  }

  getUserById(id: number): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/users/${id}`);
  }

  createUser(user: User): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/users`, user);
  }

  updateUser(user: User): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/users/${user.id}`, user);
  }

  deleteUser(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/users/${id}`);
  }
}
