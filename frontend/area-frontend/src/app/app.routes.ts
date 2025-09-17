import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { Weather } from './components/weather/weather';
import { Translate } from './components/translate/translate';
import { Users } from './components/users/users';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'weather', component: Weather },
  { path: 'translate', component: Translate },
  { path: 'users', component: Users },
  { path: '**', redirectTo: '' }
];
