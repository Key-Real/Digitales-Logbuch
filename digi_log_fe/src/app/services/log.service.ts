import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class LogService {

  constructor() { }

  log(message: any){
    if (!environment.production) { 
      console.log(message)
    }
  }

}
