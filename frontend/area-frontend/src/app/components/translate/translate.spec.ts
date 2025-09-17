import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Translate } from './translate';

describe('Translate', () => {
  let component: Translate;
  let fixture: ComponentFixture<Translate>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Translate]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Translate);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
