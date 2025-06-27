---
title: "Students"
permalink: /students/
author_profile: true
---

<style>
  .grid-3cols {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
  }
  .grid-3cols > div {
    padding: 0;
    border: none;
    background: transparent;
  }
  .alumni-list {
    list-style-type: disc;
    padding-left: 1.5rem;
  }
</style>



## PhD Students

<div class="grid-3cols">
  {% for name in site.data.students.phd %}
    <div>{{ name }}</div>
  {% endfor %}
</div>


## Master Students

<div class="grid-3cols">
  {% for name in site.data.students.master %}
    <div>{{ name }}</div>
  {% endfor %}
</div>

## Alumni

<ul class="alumni-list" style="list-style-type: none; padding-left: 0; margin-left: 0;">
  {% for name in site.data.students.alumni %}
    <li>{{ name }}</li>
  {% endfor %}
</ul>
