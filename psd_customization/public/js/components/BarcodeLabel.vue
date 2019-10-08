<template>
  <div class="root psd-barcode-label-container">
    <div :id="`barcode-${barcode}`" class="psd-barcode-label">
      <div class="psd-barcode-header">{{ company }}</div>
      <div class="psd-barcode-text">
        <span class="psd-barcode-strong">{{ item_code }}</span
        >:
        <span>{{ item_name }}</span>
      </div>
      <div class="psd-barcode-area">
        <span v-if="invalid">INVALID</span>
        <svg v-else></svg>
      </div>
      <div class="psd-barcode-foot psd-barcode-strong psd-barcode-rotated">
        {{ price_formatted }}
      </div>
    </div>
    <div class="psd-download_image" @click="download">
      <i class="glyphicon glyphicon-download-alt" />
    </div>
  </div>
</template>

<script>
import JsBarcode from 'jsbarcode';
import domtoimage from 'dom-to-image-more';

export default {
  props: [
    'barcode',
    'type',
    'company',
    'item_code',
    'item_name',
    'price_formatted',
  ],
  data: function() {
    return { invalid: false };
  },
  mounted() {
    try {
      JsBarcode(`#barcode-${this.barcode} svg`, this.barcode, {
        format: 'ean13',
        margin: 0,
        marginTop: 4,
        marginBottom: 4,
        height: 40,
        width: 2,
        fontSize: 11,
        flat: true,
      });
    } catch (e) {
      this.invalid = true;
    }
  },
  methods: {
    download: async function() {
      if (!this.invalid) {
        try {
          const dataUrl = await domtoimage.toPng(
            document.getElementById(`barcode-${this.barcode}`)
          );
          const link = document.createElement('a');
          link.href = dataUrl;
          link.download = `${this.item_code} - ${this.barcode}.png`;
          link.click();
        } catch (e) {
          console.error('oops, something went wrong!', e);
        }
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.root {
  --label-height: 34mm;
  --label-width: 64mm;
  --label-font-size: 8pt;
  --label-container-padding: 1.5mm;
  --first-row-height: 4mm;
  --last-col-width: 6mm;
}
.psd-barcode-label-container {
  position: relative;
  border: 1px solid #d1d8dd;
  width: fit-content;
  overflow: hidden;
  margin: 2px;
}
.psd-barcode-label {
  background-color: #ffffff;
  color: #000000;
  box-sizing: border-box;
  height: var(--label-height);
  width: var(--label-width);
  padding: var(--label-container-padding);
  display: grid;
  grid-template-columns: 1fr var(--last-col-width);
  grid-template-rows: var(--first-row-height) 1fr calc(var(--label-height) / 2);
  grid-template-areas:
    'header footer'
    'text footer'
    'barcode footer';
  font-family: monospace;
  font-size: var(--label-font-size);
  line-height: 1.2;
  text-align: center;
}
.psd-barcode-rotated {
  line-height: var(--last-col-width);
  transform: translate(
      calc(
        (
            var(--last-col-width) -
              (var(--label-height) - var(--label-container-padding) * 2)
          ) / 2
      ),
      0
    )
    rotate(-90deg);
  transform-origin: center center;
  height: var(--last-col-width);
  width: calc(var(--label-height) - var(--label-container-padding) * 2);
}
.psd-barcode-header {
  grid-area: header;
  text-transform: uppercase;
}
.psd-barcode-text {
  grid-area: text;
  height: calc(var(--label-font-size) * 1.2 * 3);
  overflow-y: hidden;
  align-self: center;
}
.psd-barcode-area {
  grid-area: barcode;
  align-self: center;
}
.psd-barcode-foot {
  grid-area: footer;
  font-size: 1.4em;
  align-self: center;
}
.psd-barcode-strong {
  font-weight: bold;
}
.psd-download_image {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.8);
  opacity: 0;
  font-size: 2em;
  cursor: pointer;
}
.psd-download_image:hover {
  opacity: 1;
}
</style>
