import { Component, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { NgClass } from '@angular/common';

@Component({
  selector: 'app-nav',
  imports: [RouterLink, RouterLinkActive, NgClass],
  templateUrl: './nav.html',
  styleUrl: './nav.scss'
})
export class Nav {
  protected isMenuCollapsed = signal(true);

  toggleMenu() {
    this.isMenuCollapsed.update(value => !value);
  }
}
