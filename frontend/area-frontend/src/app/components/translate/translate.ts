import { Component, signal } from '@angular/core';
import { NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Api } from '../../services/api';
import { TranslationResponse } from '../../models/api.models';

@Component({
  selector: 'app-translate',
  imports: [NgIf, FormsModule],
  templateUrl: './translate.html',
  styleUrl: './translate.scss'
})
export class Translate {
  protected text = signal<string>('');
  protected targetLang = signal<string>('en');
  protected translation = signal<TranslationResponse | null>(null);
  protected loading = signal<boolean>(false);
  protected error = signal<string | null>(null);

  constructor(private apiService: Api) {}

  translateText() {
    if (!this.text().trim()) {
      this.error.set('Veuillez entrer un texte à traduire');
      return;
    }

    if (!this.targetLang()) {
      this.error.set('Veuillez sélectionner une langue cible');
      return;
    }

    this.loading.set(true);
    this.error.set(null);
    this.translation.set(null);

    this.apiService.translateText({
      text: this.text(),
      targetLang: this.targetLang()
    }).subscribe({
      next: (data) => {
        this.translation.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Erreur lors de la traduction:', err);
        if (err.error && err.error.error) {
          this.error.set(err.error.error);
        } else {
          this.error.set('Erreur lors de la traduction. Veuillez réessayer.');
        }
        this.loading.set(false);
      }
    });
  }
}
