<template>
  <div class="first-layer">
    <div class="second-layer">
      <button @click="go_back">Назад</button>
      <div v-if="date">
        <p>{{ date }}</p>
        <ul class="info-list">
          <li v-for="value in olist" :key="value.res_st">
            Начало: {{ value.beg }} Процедура: {{ value.name }}
          </li>
        </ul>
      </div>
      <div v-else>
        <ul class="option-list">
          <li v-for="(value,ind) in olist" :key="ind">
            <button
              class="ch_option"
              @click="get_rsv(value.sch_date, value.beg + '-' + value.fin)"
            >
              {{ value.sch_date }} {{ value.beg }}-{{ value.fin }}
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
  name: "StfSide",
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
      olist: [],
      msg: "",
      date: "",
    };
  },
  created() {
    this.get_day();
  },
  methods: {
    go_back() {
      if (this.date) {
        this.get_day();
        this.date = "";
      } else {
        this.$emit("ret");
      }
    },
    mistake(detail) {
      this.msg = detail;
      document.getElementById("mypopover").showPopover();
    },
    async get_day() {
      const response = await fetch(this.defurl + "stf/day", {
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
    async get_rsv(d, t) {
      const response = await fetch(this.defurl + "stf/reservation?day=" + d, {
        headers: {
          Authorization: this.token,
        },
      });
      const data = await response.json();
      if (response.ok) {
        this.olist = data.items;
        this.date = d + " " + t;
      } else {
        this.mistake(data.detail);
      }
    },
  },
};
</script>
