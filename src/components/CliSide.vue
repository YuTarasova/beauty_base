<template>
  <div class="first-layer">
    <div class="second-layer">
      <button @click="go_back">Назад</button>
      <button @click="ch_mode">{{ o_mode }}</button>
      <div v-if="step > 9">
        <ul class="info-list">
          <li v-for="(value, ind) in olist" :key="ind">
            Дата: {{ value.res_date }} Время: {{ value.beg }}<br />
            Процедура: {{ value.name }} Цена: {{ value.price }}<br />
            Сотрудник: {{ value.last_name }} {{ value.first_name }}<br />
            Адрес: {{ value.address }}
          </li>
        </ul>
      </div>
      <div v-else-if="step === 0">
        <ul class="option-list">
          <li v-for="value in olist" :key="value.id">
            <button class="ch_option" @click="ch_city(value.tz, value.id)">
              {{ value.city_name }}
            </button>
          </li>
        </ul>
        <div class="pg-box">
          <button type="button" @click="prev" v-if="salon">Предыдущая</button>
          <p>{{ salon + 1 }}</p>
          <button type="button" @click="next" v-if="salon < staff">
            Следующая
          </button>
        </div>
      </div>
      <div v-else-if="step === 9">
        <button @click="reserve">Записаться</button>
      </div>
      <div v-else-if="step === 1">
        <ul class="option-list">
          <li v-for="value in olist" :key="value.id">
            <button class="ch_option" @click="ch_salon(value.id)">
              {{ value.address }}
            </button>
          </li>
        </ul>
      </div>
      <div v-else-if="step === 2">
        <p>Выбрать</p>
        <br />
        <button class="ch_option" @click="ch_route(true)">сотрудника...</button>
        <button class="ch_option" @click="ch_route(false)">процедуру...</button>
      </div>
      <div v-else-if="step % 3 === 0">
        <ul class="option-list">
          <li v-for="value in olist" :key="value.id">
            <button class="ch_option" @click="ch_staff(value.id)">
              {{ value.first_name }} {{ value.last_name }}
            </button>
          </li>
        </ul>
      </div>
      <div v-else-if="step < 6">
        <ul class="option-list">
          <li v-for="value in olist" :key="value.id">
            <button class="ch_option" @click="ch_type(value.id)">
              {{ value.name }} <br />
              Длительность:{{ value.dur }} Цена:{{ value.price }}
            </button>
          </li>
        </ul>
      </div>
      <div v-else-if="step === 7">
        <ul class="option-list">
          <li v-for="(value, ind) in olist" :key="ind">
            <button class="ch_option" @click="ch_day(value.sch_date)">
              {{ value.sch_date }}
            </button>
          </li>
        </ul>
      </div>
      <div v-else>
        <ul class="option-list">
          <li v-for="value in olist" :key="value.avail_st">
            <button
              class="ch_option"
              @click="time_int(value.avail_st, value.avail_end)"
            >
              {{ value.avail_st }} - {{ value.avail_end }}
            </button>
          </li>
        </ul>
        <form v-if="x" id="tform">
          <input type="number" min="0" max="23" name="hrs" required /> :
          <input type="number" min="0" max="59" name="mins" required />
          <button type="button" @click="ch_time">Выбрать</button>
        </form>
      </div>

      <div id="mypopover" popover>{{ msg }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "CliSide",
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
      o_mode: "Мои записи",
      step: 0,
      city: 0,
      tz: "",
      salon: 0,
      staff: 0,
      proc_type: 0,
      proc_day: "",
      proc_st: "",
      olist: [],
      x: undefined,
      y: undefined,
      msg: "",
    };
  },
  created() {
    const data = this.get_smth("cli/city?page=" + this.salon);
    this.staff = data.last;
  },
  methods: {
    ch_mode() {
      if (this.step < 10) {
        this.step += 10;
        this.o_mode = "Вернуться к записи";
        this.get_rsv();
      } else {
        this.go_back();
      }
    },
    go_back() {
      if (this.step === 0) {
        this.$emit("ret");
      } else {
        if (this.step > 9) {
          this.step -= 10;
          this.o_mode = "Мои записи";
        } else if (this.step === 7 || this.step === 5) {
          this.step -= 3;
        } else {
          --this.step;
        }
        switch (this.step) {
          case 0:
            this.salon = 0;
            this.staff = this.get_smth("cli/city?page=" + this.salon).last;
            break;
          case 1:
            this.get_smth("cli/salon?city_id=" + this.city);
            break;
          case 3:
            this.get_smth("cli/staff?salon_id=" + this.salon);
            break;
          case 4:
            this.get_smth("typebystaff?staff_id=" + this.staff);
            break;
          case 5:
            this.get_smth("cli/type?salon_id=" + this.salon);
            break;
          case 6:
            this.get_smth(
              "cli/staffbytype?salon_id=" +
                this.salon +
                "&type_id=" +
                this.proc_type,
            );
            break;
          case 7:
            this.get_smth(
              "cli/day?staff_id=" +
                this.staff +
                "&tz=" +
                encodeURIComponent(this.tz),
            );
            break;
          case 8:
            this.x = undefined;
            this.get_smth(
              "time?staff_id=" +
                this.staff +
                "&type_id=" +
                this.proc_type +
                "&day=" +
                this.proc_day,
            );
        }
      }
    },
    mistake(detail) {
      this.msg = detail;
      document.getElementById("mypopover").showPopover();
    },
    async get_smth(url) {
      const response = await fetch(this.defurl + url);
      const data = await response.json();
      if (response.ok) {
        this.olist = data.items;
        return data;
      }
      this.mistake(data.detail);
    },
    prev() {
      --this.salon;
      const data = this.get_smth("cli/city?page=" + this.salon);
      this.staff = data.last;
    },
    next() {
      ++this.salon;
      const data = this.get_smth("cli/city?page=" + this.salon);
      this.staff = data.last;
    },

    ch_city(tz, id) {
      this.tz = tz;
      this.city = id;
      ++this.step;
      this.get_smth("cli/salon?city_id=" + id);
    },
    ch_salon(id) {
      this.salon = id;
      ++this.step;
    },
    ch_route(b) {
      if (b) {
        ++this.step;
        this.get_smth("cli/staff?salon_id=" + this.salon);
      } else {
        this.step += 3;
        this.get_smth("cli/type?salon_id=" + this.salon);
      }
    },
    ch_staff(id) {
      this.staff = id;
      ++this.step;
      if (this.step === 4) {
        this.get_smth("typebystaff?staff_id=" + id);
      } else {
        this.get_smth(
          "cli/day?staff_id=" + id + "&tz=" + encodeURIComponent(this.tz),
        );
      }
    },
    ch_type(id) {
      this.proc_type = id;
      if (this.step === 4) {
        this.step += 3;
        this.get_smth(
          "cli/day?staff_id=" +
            this.staff +
            "&tz=" +
            encodeURIComponent(this.tz),
        );
      } else {
        ++this.step;
        this.get_smth(
          "cli/staffbytype?salon_id=" + this.salon + "&type_id=" + id,
        );
      }
    },
    ch_day(d) {
      this.x = undefined;
      this.proc_day = d;
      ++this.step;
      this.get_smth(
        "time?staff_id=" +
          this.staff +
          "&type_id=" +
          this.proc_type +
          "&day=" +
          d,
      );
    },
    time_int(beg, fin) {
      this.x = new Date("2000T" + beg);
      this.y = new Date("2000T" + fin);
    },
    ch_time() {
      const form = document.getElementById("tform");
      if (form.checkValidity()) {
        const fD = new FormData(form);
        let tmp = fD.get("hrs");
        if (tmp.length === 1) tmp = "0" + tmp;
        let t = tmp;
        tmp = fD.get("mins");
        if (tmp.length === 1) {
          t += ":0" + tmp;
        } else {
          t += ":" + tmp;
        }
        const dt = new Date("2000T" + t);
        if (this.y >= dt && dt >= this.x) {
          this.proc_st = t;
          ++this.step;
        } else {
          this.mistake("Введённое время не входит в выбранный промежуток.");
        }
      }
    },
    async reserve() {
      const response = await fetch(this.defurl + "cli/reserve", {
        method: "POST",
        headers: {
          Authorization: this.token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          staff_id: this.staff,
          res_date: this.proc_day,
          res_st: this.proc_st,
          type_id: this.proc_type,
        }),
      });
      const data = await response.json();
      this.msg = data.detail;
      document.getElementById("mypopover").showPopover();
    },
    async get_rsv() {
      const response = await fetch(this.defurl + "cli/reservation", {
        headers: {
          Authorization: this.token,
        },
      });
      const data = await response.json();
      if (response.ok) {
        this.olist = data.items;
      } else {
        this.mistake(data.detail);
      }
    },
  },
};
</script>
