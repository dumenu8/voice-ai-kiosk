import { TestBed } from '@angular/core/testing';

import { Kiosk } from './kiosk';

describe('Kiosk', () => {
  let service: Kiosk;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Kiosk);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
