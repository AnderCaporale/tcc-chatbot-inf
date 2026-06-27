import { Routes } from '@angular/router';
import { ChatComponent } from './pages/chat/chat.component';
import { PerguntasComponent } from './pages/perguntas/perguntas.component';

export const routes: Routes = [
    {
        path: "chat",
        component: ChatComponent
    },
    {
        path: "",
        component: ChatComponent
    },
    {
        path: "perguntas",
        component: PerguntasComponent
    },
];
