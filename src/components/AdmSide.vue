<template>
  <div class="first-layer">
    <div class="second-layer">
      <button @click="$emit('ret')">Выйти из аккаунта</button>
      <button @click="go_back">Назад</button>
      <button @click="reset">Сброс</button>
      <button @click="ch_mode">{{ o_mode }}</button>
      <div v-if="step === 0">
        <p>Выбрать</p>
        <br />
        <button class="ch_option" @click="ch_route(true)">сотрудника...</button>
        <button class="ch_option" @click="ch_route(false)">процедуру...</button>
      </div>
      <div v-else-if="step === 1 || step === 4">
        <ul class="option-list">
          <li v-for="value in olist" :key="value.id">
            <button class="ch_option" @click="ch_staff(value.id)">
              {{ value.first_name }} {{ value.last_name }}
            </button>
          </li>
        </ul>
      </div>
      <div v-else-if="step === 2 || step === 3">
        <ul class="option-list">
          <li v-for="value in olist" :key="value.id">
            <button class="ch_option" @click="ch_type(value.id)">
              {{ value.name }} <br />
              Длительность:{{ value.dur }} Цена:{{ value.price }}
            </button>
          </li>
        </ul>
      </div>
      <div v-else-if="step === 6">
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
          <input type="number" min="0" max="59" name="mins" required /><br />
          <label
            >Номер телефона
            <input
              type="number"
              min="10000000000"
              max="99999999999"
              name="phone"
              required
            />
          </label>
          <button type="button" @click="reserve">Записать</button>
        </form>
      </div>
      <div v-else-if="step > 6 && yad">
        {{ yad }}
        <ul class="option-list">
          <li v-for="value in olist" :key="value.id">
            <label>
              <input type="radio" name="st_list" @click="x = value.id" />
              Время:{{ value.beg }} Сотрудник: {{ value.sln }} {{ value.sfn }}
              {{ value.staff_id }}<br />
              Статус:{{ value.status }} Клиент: {{ value.cfn }} {{ value.cln }}
              {{ value.client_id }} {{ value.phone }}
            </label>
          </li>
        </ul>
        <form v-if="x" id="status-form">
          <label
            ><input
              type="radio"
              name="n_status"
              value="active"
              checked
            />Active </label
          ><br />
          <label
            ><input type="radio" name="n_status" value="absent client" />Absent
            client </label
          ><br />
          <label
            ><input
              type="radio"
              name="n_status"
              value="completed"
            />Completed </label
          ><br />
          <label
            ><input type="radio" name="n_status" value="unpaid" />Unpaid </label
          ><br />
          <label
            ><input type="radio" name="n_status" value="absent staff" />Absent
            staff </label
          ><br />
          <label
            ><input
              type="radio"
              name="n_status"
              value="interrupted"
            />Interrupted </label
          ><br />
          <label
            ><input
              type="radio"
              name="n_status"
              value="cancelled"
            />Cancelled </label
          ><br />
          <label
            ><input type="radio" name="n_status" value="other issue" />Other
            issue </label
          ><br />
          <button type="button" @click="ch_status">Изменить</button>
        </form>
      </div>
      <div v-else>
        <ul class="option-list">
          <li v-for="(value, ind) in olist" :key="ind">
            <button class="ch_option" @click="ch_day(value.sch_date)">
              {{ value.sch_date }}
            </button>
          </li>
        </ul>
      </div>
      <div id="mypopover" popover>{{ msg }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdmSide",
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
      o_mode: "Редактировать статус",
      step: 0,
      staff: 0,
      proc_type: 0,
      proc_day: "",
      olist: [],
      x: undefined,
      y: undefined,
      yad: "",
      msg: "",
    };
  },
  methods: {
    go_back() {
      if (this.step > 6) {
        this.yad = "";
        this.get_smth_adm("day");
      } else {
        if (this.step === 5 || this.step === 3) {
          this.step -= 3;
        } else if (this.step !== 0) {
          --this.step;
        }
        this.correspond_step();
      }
    },
    reset() {
      if (this.step > 6) {
        this.yad = "";
        this.get_smth_adm("day");
      } else {
        this.step = 0;
      }
    },
    ch_mode() {
      if (this.step > 6) {
        this.step -= 7;
        this.o_mode = "Редактировать статус";
        this.correspond_step();
      } else {
        this.step += 7;
        this.o_mode = "Записать посетителя";
        if (this.yad) {
          this.x = 0;
          this.get_smth_adm("reservation?day=" + this.yad);
        } else {
          this.get_smth_adm("day");
        }
      }
    },
    correspond_step() {
      if (this.step < 4) {
        switch (this.step) {
          case 1:
            this.get_smth_adm("staff");
            break;
          case 2:
            this.get_smth("typebystaff?staff_id=" + this.staff);
            break;
          case 3:
            this.get_smth_adm("type");
        }
      } else {
        switch (this.step) {
          case 4:
            this.get_smth_adm("staffbytype?type_id=" + this.proc_type);
            break;
          case 5:
            this.get_smth_adm("dayofstaff?staff_id=" + this.staff);
            break;
          case 6:
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
      } else {
        this.mistake(data.detail);
      }
    },
    async get_smth_adm(url) {
      const response = await fetch(this.defurl + "adm/" + url, {
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
    ch_route(b) {
      if (b) {
        ++this.step;
        this.get_smth_adm("staff");
      } else {
        this.step += 3;
        this.get_smth_adm("type");
      }
    },
    ch_staff(id) {
      this.staff = id;
      ++this.step;
      if (this.step === 2) {
        this.get_smth("typebystaff?staff_id=" + id);
      } else {
        this.get_smth_adm("dayofstaff?staff_id=" + id);
      }
    },
    ch_type(id) {
      this.proc_type = id;
      if (this.step === 2) {
        this.step += 3;
        this.get_smth_adm("dayofstaff?staff_id=" + this.staff);
      } else {
        ++this.step;
        this.get_smth_adm("staffbytype?type_id=" + id);
      }
    },
    ch_day(d) {
      this.x = undefined;
      if (this.step === 5) {
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
      } else {
        this.yad = d;
        this.get_smth_adm("reservation?day=" + d);
      }
    },
    time_int(beg, fin) {
      this.x = new Date("2000T" + beg);
      this.y = new Date("2000T" + fin);
    },
    async reserve() {
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
          const response = await fetch(this.defurl + "adm/reserve", {
            method: "POST",
            headers: {
              Authorization: this.token,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              staff_id: this.staff,
              phone: fD.get("phone"),
              res_date: this.proc_day,
              res_st: t,
              type_id: this.proc_type,
            }),
          });
          const data = await response.json();
          this.msg = data.detail;
        } else {
          this.msg = "Введённое время не входит в выбранный промежуток.";
        }
        document.getElementById("mypopover").showPopover();
      }
    },
    async ch_status() {
      const fD = new FormData(document.getElementById("status-form"));
      const response = await fetch(this.defurl + "adm/status", {
        method: "POST",
        headers: {
          Authorization: this.token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          status: fD.get("n_status"),
          res_id: this.x,
        }),
      });
      const data = await response.json();
      this.msg = data.detail;
      document.getElementById("mypopover").showPopover();
    },
  },
};
</script>
