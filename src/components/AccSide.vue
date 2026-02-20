<template>
  <div class="first-layer">
    <div class="second-layer">
      <button @click="go_back">Назад</button>
      <div v-if="step === 0">
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
          <button type="button" @click="ch_time">Выбрать</button>
        </form>
      </div>
      <div v-else-if="step === 1">
        Показать
        <button class="ch_option" @click="ch_route(true)">
          отработанные часы...
        </button>
        <button class="ch_option" @click="ch_route(false)">прибыль...</button>
      </div>
      <div v-else-if="step === 2">
        <ul class="info-list">
          <li v-for="value in olist" :key="value.staff_id">
            Сотрудник:{{ value.staff_id }} Часы:
            {{
              parseInt(value.hour) + Math.floor(parseInt(value.min) / 60)
            }}
            Минуты:
            {{ parseInt(value.min) % 60 }}
          </li>
        </ul>
        <div class="pg-box">
          <button type="button" @click="prev1" v-if="page">Предыдущая</button>
          <p>{{ page + 1 }}</p>
          <button type="button" @click="next1" v-if="page < maxpage">
            Следующая
          </button>
        </div>
      </div>
      <div v-else>
        <ul class="info-list">
          <li v-for="value in olist" :key="value.staff_id">
            Сотрудник:{{ value.staff_id }} Прибыль: {{ value.income }}
          </li>
        </ul>
        <div class="pg-box">
          <button type="button" @click="prev2" v-if="page">Предыдущая</button>
          <p>{{ page + 1 }}</p>
          <button type="button" @click="next2" v-if="page < maxpage">
            Следующая
          </button>
        </div>
      </div>
      <div id="mypopover" popover>{{ msg }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AccSide",
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
      page: 0,
      maxpage: 0,
      olist: [],
      st_date: "",
      end_date: "",
      msg: "",
    };
  },
  methods: {
    async get_smth(url) {
      const response = await fetch(this.defurl + "acc/" + url, {
        headers: {
          Authorization: this.token,
        },
      });
      const data = await response.json();
      if (response.ok) {
        this.olist = data.items;
        this.maxpage = data.last;
      } else {
        this.msg = data.detail;
        document.getElementById("mypopover").showPopover();
      }
    },
    ch_time() {
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
          this.st_date = st_date;
          this.end_date = end_date;
          ++this.step;
        } else {
          this.mistake("Некорректный диапазон.");
        }
      }
    },
    ch_route(b) {
      this.page = 0;
      if (b) {
        ++this.step;
        this.get_page1();
      } else {
        this.step += 2;
        this.get_page2();
      }
    },
    get_page1() {
      this.get_smth(
        "hour?sch_start=" +
          this.st_date +
          "&sch_end=" +
          this.end_date +
          "&page=" +
          this.page,
      );
    },
    get_page2() {
      this.get_smth(
        "income?start=" +
          this.st_date +
          "&end=" +
          this.end_date +
          "&page=" +
          this.page,
      );
    },
    prev1() {
      --this.page;
      this.get_page1();
    },
    next1() {
      ++this.page;
      this.get_page1();
    },
    prev2() {
      --this.page;
      this.get_page2();
    },
    next2() {
      ++this.page;
      this.get_page2();
    },
    go_back() {
      if (this.step === 0) {
        this.$emit("ret");
      } else if (this.step === 3) {
        this.step -= 2;
      } else {
        --this.step;
      }
    },
  },
};
</script>
