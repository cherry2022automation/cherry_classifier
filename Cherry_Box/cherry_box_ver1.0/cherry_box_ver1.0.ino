// 動作確認済み

#include <Wire.h>

#define SENSOR_ADRS   0x40              // GP2Y0E03のI2Cアドレス
#define DISTANCE_ADRS 0x5E              // Distance Value のデータアドレス

int led_G = 16;
int led_Y = 17;
int led_R = 5;
int sw = 2;

int sw_ON = 0;
int sw_OFF = 1;

void update_LED(int RYG){

  // LED Green
  if(RYG & 0b0001){
    digitalWrite(led_G, HIGH);
  }else{
    digitalWrite(led_G, LOW);
  }

  // LED Yellow
  if(RYG & 0b0010){
    digitalWrite(led_Y, HIGH);
  }else{
    digitalWrite(led_Y, LOW);
  }

  // LED Red
  if(RYG & 0b0100){
    digitalWrite(led_R, HIGH);
  }else{
    digitalWrite(led_R, LOW);
  }

}

int get_distance()
{
     int  ans  ;
     float ans_mm;
     byte c[2] ;

     Wire.beginTransmission(SENSOR_ADRS) ;        // 通信の開始処理
     Wire.write(DISTANCE_ADRS) ;                  // 距離値を格納したテーブルのアドレスを指定する
     ans = Wire.endTransmission() ;               // データの送信と終了処理
     if (ans == 0) {
          ans = Wire.requestFrom(SENSOR_ADRS,2) ; // GP2Y0E03にデータ送信要求をだし、2バイト受信する
          c[0] = Wire.read()  ;                   // データの11-4ビット目を読み出す
          c[1] = Wire.read()  ;                   // データの 3-0ビット目を読み出す
          ans = ((c[0]*16+c[1]) / 16) / 4 ;       // 取り出した値から距離(cm)を計算する
          ans_mm = (c[0]*16+c[1]) / 6.4;
     } else {
          ans_mm = 0;
     }
     return(ans_mm);
}

// 電源起動時とリセットの時だけのみ処理する関数
void setup()
{
     Serial.begin(9600) ;               // シリアル通信の初期化
     Wire.begin() ;                     // Ｉ２Ｃの初期化、マスターとする
     pinMode(led_G, OUTPUT);            // ピン設定
     pinMode(led_Y, OUTPUT);
     pinMode(led_R, OUTPUT);
     pinMode(sw, INPUT_PULLUP);
     delay(1000) ;                      // 1秒後に開始
}

// 繰り返し実行されるメインの処理関数
void loop()
{
     int ans_mm;
     ans_mm = get_distance();
     Serial.println(ans_mm);
     if(ans_mm < 100){
        update_LED(0b0100);
     }
     else if(ans_mm < 150){
        update_LED(0b0010);
     }
     else if(ans_mm < 300){
        update_LED(0b0001);
     }
     if (digitalRead(sw) == sw_ON){
        update_LED(0b0111);
     }
     delay(100);
}
