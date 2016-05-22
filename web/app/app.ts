import {Component, Pipe, PipeTransform} from '@angular/core';
import {bootstrap}    from '@angular/platform-browser-dynamic';
import {Http, HTTP_PROVIDERS} from '@angular/http';
import {Observable} from 'rxjs/Rx';
import {MdToolbar} from '@angular2-material/toolbar';
import {MdButton} from '@angular2-material/button';
import {MdCard} from '@angular2-material/card';
import {MdIcon} from '@angular2-material/icon';
import {MdList} from '@angular2-material/list';
import {MdProgressBar} from '@angular2-material/progress-bar';
import {MdProgressCircle} from '@angular2-material/progress-circle';

import * as moment from 'moment';

const momentConstructor: (value?: any) => moment.Moment = (<any>moment).default || moment;

@Pipe({
    name: 'momentFromNow'
})
// The work of the pipe is handled in the tranform method with our pipe's class
class MomentFromNowPipe implements PipeTransform {
    transform(value: Date | moment.Moment, ...args: any[]): any {
        const momentInstance = momentConstructor(value);
        return momentConstructor(value).from(momentConstructor());
    }
}

@Component({
    selector: 'material-app',
    templateUrl: 'app/app.html',
    directives: [MdToolbar, MdButton, MdCard, MdIcon, MdList, MdProgressBar, MdProgressCircle],
    pipes: [MomentFromNowPipe]
})
export class AppComponent {

    constructor(http: Http) {
        http.get(this.baseurl + "history")
            .subscribe(response => this.history = response.json(),
            response => {
                this.error = response.json();
                this.isError = true;
            });

        this.myHttp = http;
    }

    public myHttp: Http;

    public error: string;
    public isError: boolean = false;
    public isWatering: boolean = false;

    public baseurl: string = "http://192.168.178.22/watering.api/";

    public waterFor(duration: number): void {
        this.myHttp.get(this.baseurl + "water/" + duration)
            .subscribe(
            response => {
                this.error = response.json();
                this.isError = false;
                this.isWatering = false
            },
            response => {
                this.error = response.json();
                this.isError = true;
                this.isWatering = false;
            }
            );
    }

    public recordRefill(): void {
        /*$mdDialog.show(
     $mdDialog.alert()
     .title('Secondary Action')
     .textContent('Secondary actions can be used for one click actions')
     .ariaLabel('Secondary click demo')
     .ok('Neat!')
     .targetEvent(event)
     );
     };*/
    }

    public history = {"last_filling": {"id": 4, "quantity": 25000, "user": "Jan", "filldate": "2016-05-21T10:49:40.443778"}, "remaining": 24550, "history": [{"waterdate": "2016-05-21T10:54:32.236846", "user": "Jan", "quantity": 250}, {"waterdate": "2016-05-21T10:53:29.179629", "user": "Jan", "quantity": 100}, {"waterdate": "2016-05-21T10:52:43.296616", "user": "Jan", "quantity": 100}]};

    /*
         app.config(function ($mdThemingProvider) {
         $mdThemingProvider.theme('default')
         .primaryPalette('blue')
         .accentPalette('red');
         });
         */
}

bootstrap(AppComponent, [HTTP_PROVIDERS]);