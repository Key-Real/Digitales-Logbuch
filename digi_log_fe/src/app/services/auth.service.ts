import { Injectable } from '@angular/core';
import { CookieService } from './cookie.service';
import { CookieType } from '../interfaces';
import { HttpService } from './http.service';
import { catchError, firstValueFrom, of } from 'rxjs';
import { Router } from '@angular/router';

@Injectable({
  providedIn: "root",
})
export class AuthService {
  constructor(private cookieService:CookieService, private http:HttpService, private router: Router) {}

  TOKEN = "";

  // async getToken():Promise<string> {
  //   let token = ""
  //   if (this.TOKEN) {

  //   }else{
  //     let at = this.cookieService.getValue(CookieType.accessToken);
  //     if (at && (await firstValueFrom( this.http.validateToken(at)))) {
  //       this.TOKEN = at;
  //     } else {
  //       let rt = this.cookieService.getValue(CookieType.refreshToken);
  //       if (rt && (await firstValueFrom(this.http.validateToken(rt)))) {
  //         let req = this.http.refreshToken(rt).pipe(
  //           catchError((error) => {
  //             return of(error);
  //           })
  //         );

  //         this.TOKEN = await firstValueFrom(req);
  //         this.cookieService.addToCookie(CookieType.accessToken,this.TOKEN)
  //       } else {
  //         this.router.navigate(["/login"]);
  //       }
  //     }
  //   }
  //   return this.TOKEN
  // }


  // updateAccessToken(token:string) {

  // }
}
