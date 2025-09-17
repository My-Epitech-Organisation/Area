import { Component, OnInit, signal } from '@angular/core';
import { NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Api } from '../../services/api';
import { User } from '../../models/api.models';

@Component({
  selector: 'app-users',
  imports: [NgFor, NgIf, FormsModule],
  templateUrl: './users.html',
  styleUrl: './users.scss'
})
export class Users implements OnInit {
  protected users = signal<User[]>([]);
  protected loading = signal<boolean>(false);
  protected error = signal<string | null>(null);

  protected showUserForm = signal<boolean>(false);
  protected formLoading = signal<boolean>(false);
  protected selectedUserId = signal<number | null>(null);
  protected userForm = signal<User>({
    username: '',
    email: '',
    role: 'user'
  });

  constructor(private apiService: Api) {}

  ngOnInit() {
    this.loadUsers();
  }

  loadUsers() {
    this.loading.set(true);
    this.error.set(null);

    this.apiService.getAllUsers().subscribe({
      next: (data) => {
        this.users.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Erreur lors du chargement des utilisateurs:', err);
        this.error.set('Erreur lors du chargement des utilisateurs. Veuillez réessayer.');
        this.loading.set(false);
      }
    });
  }

  toggleUserForm() {
    if (this.showUserForm()) {
      this.showUserForm.set(false);
    } else {
      this.userForm.set({
        username: '',
        email: '',
        role: 'user'
      });
      this.showUserForm.set(true);
    }
  }

  updateUserForm(field: string, value: string) {
    this.userForm.update(form => ({
      ...form,
      [field]: value
    }));
  }

  editUser(user: User) {
    if (user.id !== undefined) {
      this.selectedUserId.set(user.id);
      this.userForm.set({
        ...user
      });
      this.showUserForm.set(true);
    }
  }

  saveUser() {
    this.formLoading.set(true);
    const userData = this.userForm();
    const userId = this.selectedUserId();

    if (userId !== null) {
      this.apiService.updateUser({
        ...userData,
        id: userId
      }).subscribe({
        next: () => {
          this.formLoading.set(false);
          this.showUserForm.set(false);
          this.loadUsers();
        },
        error: (err) => {
          console.error('Erreur lors de la mise à jour de l\'utilisateur:', err);
          this.error.set('Erreur lors de la mise à jour de l\'utilisateur.');
          this.formLoading.set(false);
        }
      });
    } else {
      this.apiService.createUser(userData).subscribe({
        next: () => {
          this.formLoading.set(false);
          this.showUserForm.set(false);
          this.loadUsers();
        },
        error: (err) => {
          console.error('Erreur lors de la création de l\'utilisateur:', err);
          this.error.set('Erreur lors de la création de l\'utilisateur.');
          this.formLoading.set(false);
        }
      });
    }
  }

  deleteUser(id: number | undefined) {
    if (id === undefined) return;

    if (confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
      this.loading.set(true);

      this.apiService.deleteUser(id).subscribe({
        next: () => {
          this.loadUsers();
        },
        error: (err) => {
          console.error('Erreur lors de la suppression de l\'utilisateur:', err);
          this.error.set('Erreur lors de la suppression de l\'utilisateur.');
          this.loading.set(false);
        }
      });
    }
  }
}
