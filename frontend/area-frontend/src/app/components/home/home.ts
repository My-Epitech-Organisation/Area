import { Component, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NgIf } from '@angular/common';
import { Api } from '../../services/api';

@Component({
  selector: 'app-home',
  imports: [RouterLink, NgIf],
  templateUrl: './home.html',
  styleUrl: './home.scss'
})
export class Home {
  protected actionMessage = signal<string | null>(null);

  constructor(private apiService: Api) {}

  triggerAction() {
    this.apiService.triggerAction().subscribe({
      next: (response) => {
        this.actionMessage.set('Action déclenchée avec succès !');
        setTimeout(() => this.actionMessage.set(null), 3000);
      },
      error: (error) => {
        console.error('Erreur lors du déclenchement de l\'action:', error);
        this.actionMessage.set('Erreur lors du déclenchement de l\'action.');
        setTimeout(() => this.actionMessage.set(null), 3000);
      }
    });
  }
}
