<template>
  <div class="first-layer">
    <div class="second-layer">
      <button @click="$emit('ret')">Выйти из аккаунта</button>
      <div v-if="step < 4">
        <button @click="sw_mode(0)">Выбор сотрудника</button>
        <button @click="sw_mode(1)">Добавление сотрудника</button>
        <button @click="sw_mode(2)">Просмотр записей</button>
        <div v-if="step === 0">
          <ul class="option-list">
            <li v-for="value in olist" :key="value.id">
              <button class="ch_option" @click="ch_staff(value.id)">
                {{ value.id }} {{ value.last_name }} {{ value.first_name }}
                {{ value.fathers_name }}
              </button>
            </li>
          </ul>
        </div>
        <div v-else-if="step === 1">
          <form id="st-reg">
            <label
              >ID<span style="color: red">*</span><br />
              <input
                type="number"
                name="staff_id"
                min="0"
                max="65535"
                required
              />
            </label>
            <br />
            <label
              >Имя<span style="color: red">*</span><br />
              <input
                type="text"
                name="first_name"
                pattern="^[А-Я][-а-яА-Я\u0020]{0,31}$"
                required
                placeholder="Введите имя"
              />
            </label>
            <br />
            <label
              >Фамилия<br />
              <input
                type="text"
                name="last_name"
                pattern="^[А-Я][-а-яА-Я\u0020]{0,31}$"
                required
                placeholder="Введите фамилию"
              />
            </label>
            <br />
            <label
              >Отчество<br />
              <input
                type="text"
                name="fathers_name"
                pattern="^[А-Я][-а-яА-Я\u0020]{0,31}$"
                placeholder="Введите отчество"
              />
            </label>
            <br />
            <label
              >Номер телефона<span style="color: red">*</span><br />
              <small
                >Формат: 00000000000<br />
                т.е. если номер +1 (234) 567-89-01, введите 12345678901</small
              ><br />
              <input
                type="number"
                name="phone"
                min="10000000000"
                max="99999999999"
                required
                placeholder="XXXXXXXXXXX"
              />
            </label>
            <br />
            <label
              >Пароль<span style="color: red">*</span><br />
              <small
                >Латинские буквы, цифры и символы '@', '#', '$', '%', '^', '~',
                '_'. Длиной от 6 до 32 символов.</small
              ><br />
              <input
                type="password"
                name="password"
                pattern="^[\w@#%~\u0024\u005e]{6,32}$"
                required
                placeholder="Введите пароль"
              />
            </label>
            <br />
            <button type="button" @click="st_reg">Добавить</button>
          </form>
        </div>
        <div v-else-if="step === 2">
          <form id="dateform">
            <label
              >Начало диапазона:
              <input
                type="number"
                min="1000"
                max="9999"
                name="styr"
                required
                placeholder="ГГГГ"
              />
              -
              <input
                type="number"
                min="1"
                max="12"
                name="stmnth"
                required
                placeholder="ММ"
              />
              -
              <input
                type="number"
                min="1"
                max="31"
                name="stday"
                required
                placeholder="ДД"
              /> </label
            ><br />
            <label>
              Конец диапазона:
              <input
                type="number"
                min="1000"
                max="9999"
                name="endyr"
                required
                placeholder="ГГГГ"
              />
              -
              <input
                type="number"
                min="1"
                max="12"
                name="endmnth"
                required
                placeholder="ММ"
              />
              -
              <input
                type="number"
                min="1"
                max="31"
                name="endday"
                required
                placeholder="ДД"
              /> </label
            ><br />
            <button type="button" @click="get_rsv">Показать записи</button>
          </form>
        </div>
        <div v-else>
          <ul class="info-list">
            <li v-for="value in olist" :key="value.id">
              Дата:{{ value.res_date }} Время:{{ value.beg }} Статус:{{
                value.status
              }}
              Клиент:{{ value.phone }} <br />Сотрудник:{{ value.staff_id }}
              {{ value.sln }} {{ value.sfn }} <br />Процедура:{{
                value.type_id
              }}
              {{ value.name }}
            </li>
          </ul>
          <div class="pg-box">
            <button type="button" @click="prev" v-if="page">Предыдущая</button>
            <p>{{ page + 1 }}</p>
            <button type="button" @click="next" v-if="page < maxpage">
              Следующая
            </button>
          </div>
        </div>
      </div>
      <div v-else>
        <button @click="sw_mode(0)">Назад</button>
        <button @click="sw_mode(4)">Удаление квалификаций</button>
        <button @click="sw_mode(5)">Добавление квалификаций</button>
        <button @click="sw_mode(6)">Удаление рабочих дней</button>
        <button @click="sw_mode(8)">Добавление рабочих дней</button>
        <div v-if="step === 4">
          <ul class="option-list">
            <li v-for="value in olist" :key="value.id">
              {{ value.name }} <br />
              Уровень подготовки:{{ value.staff_lvl }}
              <button class="act_option" @click="del_type(value.id)">
                Удалить
              </button>
            </li>
          </ul>
        </div>
        <div v-else-if="step === 5">
          <ul class="option-list">
            <li v-for="value in olist" :key="value.id">
              {{ value.name }} <br />
              Уровень подготовки:{{ value.staff_lvl }}
              <button class="act_option" @click="add_type(value.id)">
                Добавить
              </button>
            </li>
          </ul>
          <div class="pg-box">
            <button type="button" @click="prev" v-if="page">Предыдущая</button>
            <p>{{ page + 1 }}</p>
            <button type="button" @click="next" v-if="page < maxpage">
              Следующая
            </button>
          </div>
        </div>
        <div v-else-if="step === 6">
          <form id="rangeform">
            <label>
              Начало диапазона через
              <input type="number" min="0" max="365" name="st_rt" required />
              дней. </label
            ><br />
            <label>
              Диапазон:
              <input type="number" min="1" max="365" name="dur" required />
              дней.
            </label>
            <button type="button" @click="get_day">Показать</button>
          </form>
        </div>
        <div v-else-if="step === 7">
          <ul class="option-list">
            <li v-for="(value, ind) in olist" :key="ind">
              {{ value.sch_date }} {{ value.beg }}-{{ value.fin }}
              <button class="act_option" @click="del_day(value.sch_date)">
                Удалить
              </button>
            </li>
          </ul>
        </div>
        <div v-else>
          <form id="dateform2">
            <label>
              Дата:
              <input
                type="number"
                min="1000"
                max="9999"
                name="yr"
                required
                placeholder="ГГГГ"
              />
              -
              <input
                type="number"
                min="1"
                max="12"
                name="mnth"
                required
                placeholder="ММ"
              />
              -
              <input
                type="number"
                min="1"
                max="31"
                name="day"
                required
                placeholder="ДД"
              /> </label
            ><br />
            <label>
              Начало:
              <input
                type="number"
                min="0"
                max="23"
                name="sthr"
                required
                placeholder="ЧЧ"
              />
              :
              <input
                type="number"
                min="0"
                max="59"
                name="stmin"
                required
                placeholder="ММ"
              /> </label
            ><br />
            <label>
              Конец:
              <input
                type="number"
                min="0"
                max="23"
                name="endhr"
                required
                placeholder="ЧЧ"
              />
              :
              <input
                type="number"
                min="0"
                max="59"
                name="endmin"
                required
                placeholder="ММ"
              /> </label
            ><br />
            <button type="button" @click="get_rsv2">Добавить</button>
          </form>
        </div>
      </div>

      <div id="mypopover" popover>{{ msg }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "HeadSide",
  props: {
    defurl: {
      type: String,
      required: true,
    },
    token: {
      type: String,
      required: true,
    },
  },
  emits: ["ret"],
  data() {
    return {
      step: 0,
      staff: 0,
      page: 0,
      maxpage: 0,
      olist: [],
      res_start: "",
      res_end: "",
      msg: "",
    };
  },
  created() {
    this.sw_mode(0);
  },
  methods: {
    mistake(detail) {
      this.msg = detail;
      document.getElementById("mypopover").showPopover();
    },
    async get_smth(url) {
      const response = await fetch(this.defurl + "head/" + url, {
        headers: {
          Authorization: this.token,
        },
      });
      const data = await response.json();
      if (response.ok) {
        this.olist = data.items;
        return data;
      }
      this.mistake(data.detail);
    },
    sw_mode(pets) {
      this.step = pets;
      switch (pets) {
        case 0:
          this.get_smth("staff");
          break;
        case 4:
          this.get_smth("stafftype?staff_id=" + this.staff);
          break;
        case 5:
          this.page = 0;
          this.maxpage = this.get_smth(
            "type?page=0&staff_id=" + this.staff,
          ).last;
      }
    },
    ch_staff(id) {
      this.staff = id;
      this.sw_mode(4);
    },
    async st_reg() {
      let form = document.getElementById("st-reg");
      if (form.checkValidity()) {
        const fD = new FormData(form);
        const response = await fetch(this.defurl + "head/register", {
          method: "POST",
          headers: {
            Authorization: this.token,
          },
          body: fD,
        });
        const data = await response.json();
        this.msg = data.detail;
        if (response.ok) {
          form.reset();
        }
        document.getElementById("mypopover").showPopover();
      }
    },
    get_rsv() {
      const form = document.getElementById("dateform");
      if (form.checkValidity()) {
        const fD = new FormData(form);
        let tmp = fD.get("stmnth");
        let st_date =
          tmp.length === 1
            ? fD.get("styr") + "-0" + tmp
            : fD.get("styr") + "-" + tmp;
        tmp = fD.get("stday");
        if (tmp.length === 1) {
          st_date += "-0" + tmp;
        } else {
          st_date += "-" + tmp;
        }
        tmp = fD.get("endmnth");
        let end_date =
          tmp.length === 1
            ? fD.get("endyr") + "-0" + tmp
            : fD.get("endyr") + "-" + tmp;
        tmp = fD.get("endday");
        if (tmp.length === 1) {
          end_date += "-0" + tmp;
        } else {
          end_date += "-" + tmp;
        }
        if (new Date(end_date) >= new Date(st_date)) {
          this.page = 0;
          this.res_start = st_date;
          this.res_end = end_date;
          ++this.step;
          this.maxpage = this.get_smth(
            "reservation?page=0&res_start=" + st_date + "&res_end=" + end_date,
          ).last;
        } else {
          this.mistake("Некорректный диапазон.");
        }
      }
    },
    get_page() {
      if (this.step === 3) {
        this.maxpage = this.get_smth(
          "reservation?res_start=" +
            this.res_start +
            "&res_end=" +
            this.res_end +
            "&page=" +
            this.page,
        ).last;
      } else {
        this.maxpage = this.get_smth(
          "type?staff_id=" + this.staff + "&page=" + this.page,
        ).last;
      }
    },
    prev() {
      --this.page;
      this.get_page();
    },
    next() {
      ++this.page;
      this.get_page();
    },
    async del_type(id) {
      const response = await fetch(this.defurl + "head/type", {
        method: "DELETE",
        headers: {
          Authorization: this.token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          staff_id: this.staff,
          type_id: id,
        }),
      });
      const data = await response.json();
      this.mistake(data.detail);
    },
    async add_type(id) {
      const response = await fetch(this.defurl + "head/type", {
        method: "POST",
        headers: {
          Authorization: this.token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          staff_id: this.staff,
          type_id: id,
        }),
      });
      const data = await response.json();
      this.mistake(data.detail);
    },
    get_day() {
      const form = document.getElementById("rangeform");
      if (form.checkValidity()) {
        const fD = new FormData(form);
        ++this.step;
        this.get_smth(
          "day?staff_id=" +
            this.staff +
            "&start=" +
            fD.get("st_rt") +
            "&dur=" +
            fD.get("dur"),
        );
      } else {
        this.mistake("Некорректно введено количество дней.");
      }
    },
    async del_day(d) {
      const response = await fetch(this.defurl + "head/day", {
        method: "DELETE",
        headers: {
          Authorization: this.token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          staff_id: this.staff,
          date: d,
        }),
      });
      const data = await response.json();
      this.mistake(data.detail);
    },
    async get_rsv2() {
      const form = document.getElementById("dateform2");
      if (form.checkValidity()) {
        const fD = new FormData(form);
        let tmp = fD.get("mnth");
        let sch_date =
          tmp.length === 1
            ? fD.get("yr") + "-0" + tmp
            : fD.get("yr") + "-" + tmp;
        tmp = fD.get("day");
        if (tmp.length === 1) {
          sch_date += "-0" + tmp;
        } else {
          sch_date += "-" + tmp;
        }
        tmp = fD.get("sthr");
        if (tmp.length === 1) tmp = "0" + tmp;
        let st_t = tmp;
        tmp = fD.get("stmin");
        if (tmp.length === 1) {
          st_t += ":0" + tmp;
        } else {
          st_t += ":" + tmp;
        }
        tmp = fD.get("endhr");
        if (tmp.length === 1) tmp = "0" + tmp;
        let end_t = tmp;
        tmp = fD.get("endmin");
        if (tmp.length === 1) {
          end_t += ":0" + tmp;
        } else {
          end_t += ":" + tmp;
        }
        if (
          new Date(sch_date) &&
          new Date("2000T" + end_t) > new Date("2000T" + st_t)
        ) {
          const response = await fetch(this.defurl + "head/day", {
            method: "POST",
            headers: {
              Authorization: this.token,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              staff_id: this.staff,
              sch_date: sch_date,
              sch_st: st_t,
              sch_end: end_t,
            }),
          });
          const data = await response.json();
          this.mistake(data.detail);
        } else {
          this.mistake("Некорректная дата/временной диапазон.");
        }
      }
    },
  },
};
</script>
