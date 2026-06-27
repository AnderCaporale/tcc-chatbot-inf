import { Component, ElementRef, inject, ViewChild } from '@angular/core';
import { Utils } from '../../utils';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { marked } from 'marked';

interface ChatMessage {
  text: string;
  role: 'user' | 'assistant';
  time: string;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css'],
  imports: [ ]
})
export class ChatComponent {
  private sanitizer: DomSanitizer = inject(DomSanitizer)
  @ViewChild('messages') messagesContainer!: ElementRef;
  
  inputText = '';
  isTyping = false;

  selectedAlg = 'direct';
  selectedModel = 'gpt5';

  resposta: string = "";
  isLoading: boolean = false;

  messagesList: ChatMessage[] = [
    {
      text: 'Olá! Sou um assistente para ajudar a tirar suas dúvidas sobre o Instituto de Informática da UFRGS. Em que posso ajudar hoje?',
      role: 'assistant',
      time: Utils.formatarDataHora()
    },
  ];

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  private scrollToBottom() {
    try {
      const el = this.messagesContainer.nativeElement;
      el.scrollTop = el.scrollHeight;
    } catch (err) {
      console.error('Erro ao rolar:', err);
    }
  }


  onEnter(event: Event) {
    let mensagemValue = (<HTMLInputElement>document.getElementById("mensagem-textarea")).value;
    
    if (!this.isLoading && mensagemValue.trim()) {
      event.preventDefault();
      this.enviar();
    }
  }

  enviar() {
    let mensagemElement = (<HTMLInputElement>document.getElementById("mensagem-textarea"));

    if (!this.isLoading && mensagemElement.value.trim()) {
      let algoritmo = (<HTMLInputElement>document.getElementById("algoritmo-select")).value;
      let llm = (<HTMLInputElement>document.getElementById("llm-select")).value;
      let userId = (<HTMLInputElement>document.getElementById("userId")).value;
      this.addUserMessage(mensagemElement.value)
      this.sendData(mensagemElement.value, algoritmo, llm, userId);
      mensagemElement.value = "";
    }
  }

  addUserMessage(mensagem: string){
    const newMessage: ChatMessage = {
      text: mensagem,
      role: 'user',
      time: Utils.formatarDataHora()
    }

    this.messagesList.push(newMessage);
  }

  sendData(mensagem:string, algoritmo:string, llm:string, userId:string) {
    this.isLoading = true;
    
    const data = {
      input: {
        input_user: mensagem,
      },
      config: {
        id: userId,
        model_llm: llm,
        algoritmo: algoritmo,
      }
    };

    fetch(`http://localhost:8000/chat-with-history`, {
      method: "POST",
      body: JSON.stringify(data)
    })
    .then(async response => {
      let resultString = await response.json();


      console.log(resultString)
      const resultdoHTML = await marked.parse(resultString);
      this.sanitizer.bypassSecurityTrustHtml(resultdoHTML);

      console.log(resultdoHTML)

      const newMessage: ChatMessage = {
        text: resultdoHTML,
        role: 'assistant',
        time: Utils.formatarDataHora()
      } 
      this.messagesList.push(newMessage)

    })
    .catch(erro => {
      console.log(erro)
      this.resposta = "Erro na solicitação";
    })
    .finally(() => {
      this.isLoading = false;
    })
  }

  limpar_historico(){
    this.isLoading = true;
    let userId = (<HTMLInputElement>document.getElementById("userId")).value;

    fetch(`http://localhost:8000/limpar-historico/${userId}`, {
      method: "POST",
    })
      .then(async response => {
        this.messagesList = [];
      })
      .catch(erro => {
        console.log(erro)
        this.resposta = "Erro na solicitação";
      })
      .finally(() => {
        this.isLoading = false;
      })
  }
}