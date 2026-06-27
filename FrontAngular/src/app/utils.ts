export class Utils {

    static formatarDataHora(): string {
        const date = new Date();
        const dia = String(date.getDate()).padStart(2, '0');
        const mes = String(date.getMonth() + 1).padStart(2, '0');
        const hora = String(date.getHours()).padStart(2, '0');
        const min = String(date.getMinutes()).padStart(2, '0');

        return `${dia}/${mes} - ${hora}:${min}`;
    }

    static processarResultado(entrada:string){
        console.log(entrada)
        const textLines = entrada.replace(/\n/g, '<br>');
        const textStrong = textLines.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        console.log(textStrong)
        return textStrong;
    }
}