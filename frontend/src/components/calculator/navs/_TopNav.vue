// SPDX-License-Identifier: AGPL-3.0-or-later
<script setup>
  import ButtonComp from "@/components/personal/ButtonComp.vue";
</script>

<template>
  <header class="header row mb-0">
    <div class="col-xl-3 col-xs-12 col-sm-12 col-md-12 logo-container">
      <div class="logo">Solar Power Calculator</div>
    </div>
    <div class="col-xs-12 col-sm-12 col-md-12 col-xl-6 mt-md-4">
      <nav class="nav-links header-links my-md-auto">
        <div class="d-flex flex-row d-none d-xl-block"></div>
        <div class="card border-0 neomorphic text-purple p-2 additional-button-group justify-content-around">
          <button-comp
              title=""
              type="button"
              class="neomorphic right-angle p-2 p-sm-3 p-md-4 p-xl-2 text-purple"
              data-bs-toggle="modal"
              href="#CurrentMonthStatsModal"
              role="button"
              aria-label="Current month stats">
            <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-graph-up additional-button-icon" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M0 0h1v15h15v1H0zm14.817 3.113a.5.5 0 0 1 .07.704l-4.5 5.5a.5.5 0 0 1-.74.037L7.06 6.767l-3.656 5.027a.5.5 0 0 1-.808-.588l4-5.5a.5.5 0 0 1 .758-.06l2.609 2.61 4.15-5.073a.5.5 0 0 1 .704-.07"/>
            </svg>
          </button-comp>
          <button-comp
              title=""
              class="neomorphic right-angle p-2 p-sm-3 p-md-4 p-xl-2 text-purple"
              data-bs-toggle="modal"
              href="#PowerGenerationByMonthModal"
              role="button"
              aria-label="Power generation by month">
            <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-file-bar-graph-fill additional-button-icon" viewBox="0 0 16 16">
              <path d="M12 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2m-2 11.5v-6a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5m-2.5.5a.5.5 0 0 1-.5-.5v-4a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-.5.5zm-3 0a.5.5 0 0 1-.5-.5v-2a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-.5.5z"/>
            </svg>
          </button-comp>
          <button-comp
              title=""
              class="neomorphic right-angle p-2 p-sm-3 p-md-4 p-xl-2 text-purple"
              data-bs-toggle="modal"
              href="#CurrentYearStatsModal"
              role="button"
              aria-label="Power generation by years">
            <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-stack additional-button-icon" viewBox="0 0 16 16">
              <path d="m14.12 10.163 1.715.858c.22.11.22.424 0 .534L8.267 15.34a.6.6 0 0 1-.534 0L.165 11.555a.299.299 0 0 1 0-.534l1.716-.858 5.317 2.659c.505.252 1.1.252 1.604 0l5.317-2.66zM7.733.063a.6.6 0 0 1 .534 0l7.568 3.784a.3.3 0 0 1 0 .535L8.267 8.165a.6.6 0 0 1-.534 0L.165 4.382a.299.299 0 0 1 0-.535z"/>
              <path d="m14.12 6.576 1.715.858c.22.11.22.424 0 .534l-7.568 3.784a.6.6 0 0 1-.534 0L.165 7.968a.299.299 0 0 1 0-.534l1.716-.858 5.317 2.659c.505.252 1.1.252 1.604 0z"/>
            </svg>
          </button-comp>
          <button-comp
              title=""
              class="neomorphic right-angle p-2 p-sm-3 p-md-4 p-xl-2 text-purple"
              data-bs-toggle="modal"
              href="#CalendarModal"
              role="button"
              aria-label="Full period analytics">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-calendar-date additional-button-icon" viewBox="0 0 16 16">
              <path d="M6.445 11.688V6.354h-.633A13 13 0 0 0 4.5 7.16v.695c.375-.257.969-.62 1.258-.777h.012v4.61zm1.188-1.305c.047.64.594 1.406 1.703 1.406 1.258 0 2-1.066 2-2.871 0-1.934-.781-2.668-1.953-2.668-.926 0-1.797.672-1.797 1.809 0 1.16.824 1.77 1.676 1.77.746 0 1.23-.376 1.383-.79h.027c-.004 1.316-.461 2.164-1.305 2.164-.664 0-1.008-.45-1.05-.82zm2.953-2.317c0 .696-.559 1.18-1.184 1.18-.601 0-1.144-.383-1.144-1.2 0-.823.582-1.21 1.168-1.21.633 0 1.16.398 1.16 1.23"/>
              <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5M1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4z"/>
            </svg>
          </button-comp>
          <button-comp
              title=""
              class="neomorphic right-angle p-2 p-sm-3 p-md-4 p-xl-2 text-purple"
              data-bs-toggle="modal"
              href="#SystemLogsModal"
              role="button"
              aria-label="SystemLogsLabel">
            <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-list-columns-reverse additional-button-icon" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M0 .5A.5.5 0 0 1 .5 0h2a.5.5 0 0 1 0 1h-2A.5.5 0 0 1 0 .5m4 0a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1h-10A.5.5 0 0 1 4 .5m-4 2A.5.5 0 0 1 .5 2h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5m4 0a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5m-4 2A.5.5 0 0 1 .5 4h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5m4 0a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5m-4 2A.5.5 0 0 1 .5 6h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5m4 0a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 0 1h-8a.5.5 0 0 1-.5-.5m-4 2A.5.5 0 0 1 .5 8h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5m4 0a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 0 1h-8a.5.5 0 0 1-.5-.5m-4 2a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5m4 0a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1h-10a.5.5 0 0 1-.5-.5m-4 2a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5m4 0a.5.5 0 0 1 .5-.5h6a.5.5 0 0 1 0 1h-6a.5.5 0 0 1-.5-.5m-4 2a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5m4 0a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5"/>
            </svg>
          </button-comp>
          <button-comp title="" class="neomorphic right-angle p-2 p-sm-3 p-md-4 p-xl-2 text-purple">
            <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-info-square-fill additional-button-icon" viewBox="0 0 16 16">
              <path d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2zm8.93 4.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533zM8 5.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2"/>
            </svg>
          </button-comp>
          <button-comp to="/" title="" class="neomorphic right-angle p-2 p-sm-3 p-md-4 p-xl-2 text-purple">
            <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-person-raised-hand additional-button-icon" viewBox="0 0 16 16">
              <path d="M6 6.207v9.043a.75.75 0 0 0 1.5 0V10.5a.5.5 0 0 1 1 0v4.75a.75.75 0 0 0 1.5 0v-8.5a.25.25 0 1 1 .5 0v2.5a.75.75 0 0 0 1.5 0V6.5a3 3 0 0 0-3-3H6.236a1 1 0 0 1-.447-.106l-.33-.165A.83.83 0 0 1 5 2.488V.75a.75.75 0 0 0-1.5 0v2.083c0 .715.404 1.37 1.044 1.689L5.5 5c.32.32.5.754.5 1.207"/>
              <path d="M8 3a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3"/>
            </svg>
          </button-comp>
          <button-comp title="" href="https://github.com/ychernyshev/portfolio--personal-suite" class="neomorphic right-angle p-2 p-sm-3 p-md-4 p-xl-2 text-purple" target="_blank">
            <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-github additional-button-icon" viewBox="0 0 16 16">
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8"/>
            </svg>
          </button-comp>
        </div>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  grid-area: header;
  margin-bottom: 1.4rem;
}

.header-links {
  display: flex;
  flex-direction: row;
  width: 100%;
  justify-content: center;
  align-items: center;
}

.logo-container {
  display: flex;
  justify-content: center;
}

.logo {
  width: 100%;
  padding: 1rem 2rem 1rem;
  text-align: center;
  background: linear-gradient(var(--sunrise-yelow), var(--sunset-yelow));
  border-radius: 3.3rem;
  color: var(--shadow-light);
  font-weight: 300;
  font-size: 1.2rem;
  box-shadow: 0.5rem 0.5rem 1.5rem 0 var(--sunset-yelow);
}

.additional-button-group {
  flex-direction: row;
  transition: 0.2s;
  width: 100%;
  font-size: 0.9rem;
}

.additional-button-icon {
  width: 20px;
  height: 20px;
  transition: 0.2s;
}

@media (min-width: 576px) {
  .logo {
    width: 70%;
  }

  .additional-button-group {
    width: 90%;
  }
}

@media (min-width: 768px) {
  .logo {
    width: 65%;
  }

  .additional-button-group {
    width: 65%;
  }

  .additional-button-icon {
    width: 15px;
    height: 15px;
    transition: 0.2s;
  }
}


@media (min-width: 1200px) {
  .logo-container {
    justify-content: start;
  }

  .logo {
    width: 100%;
  }

  .header-links {
    justify-content: space-between;
  }

  .additional-button-group {
    width: 65%;
  }

  .additional-button-icon {
    width: 18px;
    height: 18px;
  }
}

@media (min-width: 1400px) {
  .logo {
    width: 82%;
  }

  .additional-button-group {
    width: 40%;
  }
}
</style>