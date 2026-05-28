/** @odoo-module **/

import { SearchModel } from "@web/search/search_model";
import { rankInterval } from "@web/search/utils/dates";
import { patch } from "@web/core/utils/patch";
import { serializeDate, serializeDateTime } from "@web/core/l10n/dates";
import { browser } from "@web/core/browser/browser";
import { useState, onWillStart, onMounted } from "@odoo/owl";
import { Domain } from "@web/core/domain";
import { SearchArchParser } from "./search_arch_parser";
import { useBus, useService } from "@web/core/utils/hooks";
const { DateTime } = luxon;
import { sortBy, groupBy } from "@web/core/utils/arrays";
import { toRaw } from "@odoo/owl";
import { deepCopy } from "@web/core/utils/objects";
const _xmlid = ["hr_plus.menu_hr_plus_attendance_root", "base.menu_management", "autonsi_sales_eco.menu_autonsi_sales_eco_root"];
patch(SearchModel.prototype, {

  /**
     * HOOK METHOD: Cho phép các module khác override để set giá trị mặc định
     * @param {Object} category - Thông tin về category (field name, type, etc.)
     * @param {Array} options - Danh sách các giá trị option trả về từ server
     * @returns {Number|null} - Trả về ID muốn select, hoặc null nếu không muốn can thiệp
     */
  _getCustomDefaultValue(category, options) {
    // Mặc định return null để giữ nguyên logic gốc
    return null;
  },
  async setup() {
    this.uiService = useService("ui");

    this.menuService = useService("menu");
    this.router = useService("router");
    this.buttonClick = false;

    // this.menuServices = [this.menuService
    //   .getApps()
    //   .find((menu) => menu.xmlid === _xmlid[0]), this.menuService
    //     .getApps()
    //     .find((menu) => menu.xmlid === _xmlid[1]), this.menuService
    //       .getApps()
    //       .find((menu) => menu.xmlid === _xmlid[2])];

    this.default_no_data_btn = false;
    this.searchDomain = [];
    this.searchDomainTemp = [];
    this.originDomainTemp = [];
    this.button_view_clicked = false;
    this.button_view_clicked_temp = true;
    super.setup(...arguments);
    this.isShipnoMulti = false;
    this.isCustomerMulti = false;
    this.isHasCustomer = false;
    this.isFetchFillter = false;
    this.isFetchSearchBar = false;
    this.sh_hide = true;
    this.btn_sh_hide = true;
    if (this.env.config.viewType === "list")
      //Non-list hides btn
      this.btn_sh_hide = false;
    this.options_customer = [];
    this.options_outsourcing = [];
    this.search_panel_follows = useService("search_panel_follows");
    this.is_diff_action = false;
    this.can_reload_section = true;

    onMounted(() => {
      const gs = this.env?.__getOrderBy__?._callbacks;
      if (gs && gs.length) {
        this.listController = gs[0].owner;
        this.listController.doneViewBtnCallBack = this.doneViewBtnCallBack;
      }
    });
  },

  checkAppIdInTree(node, targetAppId) {
    if (node) {
      // Kiểm tra appID của node hiện tại (bao gồm root)
      if (node.actionID === targetAppId) {
        return true;
      }

      // Đệ quy kiểm tra các children
      if (node.childrenTree && node.childrenTree.length > 0) {
        for (let child of node.childrenTree) {
          if (this.checkAppIdInTree(child, targetAppId)) {
            return true;
          }
        }
      }
      return false;
    }
    return false;
  },

  doneViewBtnCallBack() { },

  async applyView(is_no_data) {
    // if (is_no_data) {
    //   this.can_reload_section = true;
    //   this.button_view_clicked_temp = true;
    //   await this._notify();
    //   this.button_view_clicked = false;
    //   return;
    // }
    // localStorage.removeItem("N:CanLoad");
    // this.buttonClick = true;
    // this.can_reload_section = true;
    // this.button_view_clicked = true;
    // this.button_view_clicked_temp = true;
    // this.listController.model.isLoadFirst = true;
    // await this._notify();
  },

  async _notify(is_search_bar = false) {
    if (this.resModel.startsWith("document")) {
      return super._notify(...arguments);
    }
    if (this.blockNotification) {
      return;
    }
    this._reset();
    if (!is_search_bar) await this._reloadSections();
    this.trigger("update");
    this.uiService.searchPanelSelect = false;
  },

  _getDomain(params = {}) {
    if (this.resModel.startsWith("document")) {
      return super._getDomain(...arguments);
    }
    let domain = super._getDomain(params);
    this.searchDomainTemp = deepCopy(domain);
    this._setDefaultDateRange(1, false, domain, 1);

    // Nếu originDomain chưa được set, lưu lại domain hiện tại
    if (this.default_no_data_btn || this.context?.default_no_data_v2) {
      if (this.env.services.action.isRestore && this.context.save_current_action) { }
      else
        domain = [...domain, ["id", "=", "0"]];
    }
    this.env.services.action.isRestore = false

    if (this.originDomain == undefined) {
      this.originDomain = deepCopy(domain);

    }
    if (this.originDomain != undefined) {
      if (this.context?.default_no_data_v2) {
        if (JSON.stringify(domain) !== JSON.stringify(this.originDomain)) {
          domain = domain.filter(
            (item) =>
              !(
                Array.isArray(item) &&
                item.length === 3 &&
                item[0] === "id" &&
                item[1] === "=" &&
                item[2] === "0"
              )
          );
        }
      }
      else {

        // Nếu originDomain đã tồn tại, kiểm tra sự khác biệt
        if (this.buttonClick) {
          domain = domain.filter(
            (item) =>
              !(
                Array.isArray(item) &&
                item.length === 3 &&
                item[0] === "id" &&
                item[1] === "=" &&
                item[2] === "0"
              )
          );
          this.originDomainTemp = deepCopy(domain);
        }
        if (JSON.stringify(domain) !== JSON.stringify(this.originDomain)) {
          // if (this.context?.default_no_data)
          //   // Xóa ['id', '=', '0'] khỏi domain
          //   domain = domain.filter(
          //     (item) =>
          //       !(
          //         Array.isArray(item) &&
          //         item.length === 3 &&
          //         item[0] === "id" &&
          //         item[1] === "=" &&
          //         item[2] === "0"
          //       )
          //   );
          // else


          if (this.default_no_data_btn) {
            if (this.button_view_clicked) {
              this.button_view_clicked = false;
              this.button_view_clicked_temp = false;
              // Xóa ['id', '=', '0'] khỏi domain
              domain = domain.filter(
                (item) =>
                  !(
                    Array.isArray(item) &&
                    item.length === 3 &&
                    item[0] === "id" &&
                    item[1] === "=" &&
                    item[2] === "0"
                  )
              );
              this.originDomainTemp = deepCopy(domain);
            }
          }
        } else {
          if (this.context?.default_no_data_v2) return;
          if (params.reloadSection == undefined) {
            this.buttonClick = false;
            this.applyView(true);
          }
        }
      }

    }

    if (this.button_view_clicked_temp == false) {
      return this.originDomainTemp;
    }
    return domain;
  },

  _getSearchPanelDomain() {
    const domain = super._getSearchPanelDomain();
    return domain;
  },

  _getDisplay(display = {}) {
    const { viewTypes } = this.searchPanelInfo;
    const { bannerRoute, viewType } = this.env.config;
    let res = super._getDisplay(display);
    let show_sp =
      this.sections.size &&
      (!viewType || viewTypes.includes(viewType)) &&
      ("searchPanel" in display ? display.searchPanel : true);
    if ("from_dialog" in display && !viewTypes.includes("search"))
      show_sp = false;

    res.searchPanel = show_sp;
    return res;
  },

  async _reloadSections2() {
    this.blockNotification = true;

    // Check whether the search domain changed
    const searchDomain = this._getDomain({
      withSearchPanel: false,
      reloadSection: true,
    });
    const searchDomainChanged =
      this.searchPanelInfo.shouldReload ||
      JSON.stringify(this.searchDomain) !== JSON.stringify(searchDomain);
    this.searchDomain = searchDomain;

    // Check whether categories/filters will force a reload of the sections
    // const toFetch = (section) =>
    //   section.enableCounters || (searchDomainChanged && !section.expand);

    // const categoriesToFetch = this.categories.filter(toFetch);
    const categoriesToFetch = this.categories;
    // const filtersToFetch = this.filters.filter(toFetch);
    const filtersToFetch = this.filters;
    if (
      searchDomainChanged ||
      Boolean(categoriesToFetch.length + filtersToFetch.length)
    ) {
      if (this.display.searchPanel) {
      }
      // If no current search panel: will try to reload on next model update
      this.searchPanelInfo.shouldReload = !this.display.searchPanel;
    }
    this.blockNotification = false;
    if (this.header_domain) {
      this._domain = this.domain.concat(this.header_domain);
    }
  },

  async _reloadSections() {
    if (this.resModel.startsWith("document")) {

      return super._reloadSections(...arguments);
    }
    this.blockNotification = true;

    // Check whether the search domain changed
    const searchDomain = this._getDomain({
      withSearchPanel: false,
      reloadSection: true,
    });
    const searchDomainChanged =
      this.searchPanelInfo.shouldReload ||
      JSON.stringify(this.searchDomain) !== JSON.stringify(searchDomain);
    this.searchDomain = searchDomain;
    // Check whether categories/filters will force a reload of the sections
    // const toFetch = (section) =>
    //   section.enableCounters || (searchDomainChanged && !section.expand);

    // const categoriesToFetch = this.categories.filter(toFetch);
    const categoriesToFetch = this.categories;
    // const filtersToFetch = this.filters.filter(toFetch);
    const filtersToFetch = this.filters;
    if (
      searchDomainChanged ||
      Boolean(categoriesToFetch.length + filtersToFetch.length)
    ) {
      if (this.display.searchPanel) {
        this.sectionsPromise = this._fetchSections(
          categoriesToFetch,
          filtersToFetch
        );
        if (this._shouldWaitForData(searchDomainChanged)) {
          await this.sectionsPromise;
        }
      }
      // If no current search panel: will try to reload on next model update
      this.searchPanelInfo.shouldReload = !this.display.searchPanel;
    }
    this.blockNotification = false;
    if (this.header_domain) {
      this._domain = this.domain.concat(this.header_domain);
    }
  },

  async load(config) {

    const { resModel } = config;
    if (resModel.startsWith("document")) {
      return super.load(...arguments);
    }
    if (!resModel) {
      throw Error(`SearchPanel config should have a "resModel" key`);
    }
    this.resModel = resModel;

    // used to avoid useless recomputations
    this._reset();

    const { comparison, context, domain, groupBy, hideCustomGroupBy, orderBy } =
      config;

    this.globalComparison = comparison;
    this.globalContext = toRaw(Object.assign({}, context));
    this.globalDomain = domain || [];
    this.globalGroupBy = groupBy || [];
    this.globalOrderBy = orderBy || [];
    this.hideCustomGroupBy = hideCustomGroupBy;

    this.searchMenuTypes = new Set(
      config.searchMenuTypes || ["filter", "groupBy", "favorite"]
    );

    let {
      irFilters,
      loadIrFilters,
      searchViewArch,
      searchViewFields,
      searchViewId,
    } = config;
    const loadSearchView =
      searchViewId !== undefined &&
      (!searchViewArch || !searchViewFields || (!irFilters && loadIrFilters));

    const searchViewDescription = {};
    if (loadSearchView) {
      const result = await this.viewService.loadViews(
        {
          context: this.globalContext,
          resModel,
          views: [[searchViewId, "search"]],
        },
        {
          actionId: this.env.config.actionId,
          loadIrFilters: loadIrFilters || false,
        }
      );
      Object.assign(searchViewDescription, result.views.search);
      searchViewFields = searchViewFields || result.fields;
    }
    if (searchViewArch) {
      searchViewDescription.arch = searchViewArch;
    }
    if (irFilters) {
      searchViewDescription.irFilters = irFilters;
    }
    if (searchViewId !== undefined) {
      searchViewDescription.viewId = searchViewId;
    }
    this.searchViewArch = searchViewDescription.arch || "<search/>";
    this.searchViewFields = searchViewFields || {};
    if (searchViewDescription.irFilters) {
      this.irFilters = searchViewDescription.irFilters;
    }
    if (searchViewDescription.viewId !== undefined) {
      this.searchViewId = searchViewDescription.viewId;
    }

    const { searchDefaults, searchPanelDefaults } =
      this._extractSearchDefaultsFromGlobalContext();

    if (config.state) {
      this._importState(config.state);
      this.__legacyParseSearchPanelArchAnyway(
        searchViewDescription,
        searchViewFields
      );
      this.display = this._getDisplay(config.display);
      if (!this.searchPanelInfo.loaded) {
        return this._reloadSections();
      }
      if (this.display.searchPanel) {
        // if (this.env.config.viewType == "list" && this.context?.default_no_data_v2 != 1) {
        //   if (this.context.splited_tree || this.context.splited_tree_diff_model) {
        //     this.default_no_data_btn = false;
        //   } else {
        //     if (this.context.disable_view_btn) {
        //       this.default_no_data_btn = false;
        //     }
        //     else {
        //       const currentApp = this.menuService.getCurrentApp();
        //       if (currentApp == undefined) {
        //         if (this.context.disable_view_btn) {
        //           this.default_no_data_btn = false;
        //         }
        //         else if (
        //           !this.checkAppIdInTree(
        //             this.menuServices[0],
        //             this.env.config.actionId
        //           ) &&
        //           !this.checkAppIdInTree(
        //             this.menuServices[1],
        //             this.env.config.actionId
        //           ) && !this.checkAppIdInTree(
        //             this.menuServices[2],
        //             this.env.config.actionId
        //           )
        //         )
        //           this.default_no_data_btn = true;
        //       } else if (
        //         currentApp.xmlid != _xmlid[0] &&
        //         currentApp.xmlid != _xmlid[1] &&
        //         currentApp.xmlid != _xmlid[2]
        //       ) {
        //         this.default_no_data_btn = true;
        //       }
        //     }
        //   }
        // }
      }

      return;
    }

    this.blockNotification = true;

    this.searchItems = {};
    this.query = [];

    this.nextId = 1;
    this.nextGroupId = 1;
    this.nextGroupNumber = 1;

    const parser = new SearchArchParser(
      searchViewDescription,
      searchViewFields,
      searchDefaults,
      searchPanelDefaults
    );
    const { labels, preSearchItems, searchPanelInfo, sections } =
      parser.parse();

    this.searchPanelInfo = {
      ...searchPanelInfo,
      loaded: false,
      shouldReload: false,
    };

    await Promise.all(labels.map((cb) => cb(this.orm)));

    // prepare search items (populate this.searchItems)
    for (const preGroup of preSearchItems || []) {
      this._createGroupOfSearchItems(preGroup);
    }
    this.nextGroupNumber =
      1 +
      Math.max(
        ...Object.values(this.searchItems).map((i) => i.groupNumber || 0),
        0
      );

    const dateFilters = Object.values(this.searchItems).filter(
      (searchElement) => searchElement.type === "dateFilter"
    );
    if (dateFilters.length) {
      this._createGroupOfComparisons(dateFilters);
    }

    const { dynamicFilters } = config;
    if (dynamicFilters) {
      this._createGroupOfDynamicFilters(dynamicFilters);
    }

    const defaultFavoriteId = this._createGroupOfFavorites(
      this.irFilters || []
    );
    const activateFavorite =
      "activateFavorite" in config ? config.activateFavorite : true;

    // activate default search items (populate this.query)
    this._activateDefaultSearchItems(
      activateFavorite ? defaultFavoriteId : null
    );

    // prepare search panel sections

    /** @type Map<number,Section> */
    this.sections = new Map(sections || []);
    this.display = this._getDisplay(config.display);

    // console.log('SearchModel: searchPanelInfo', this.display.searchPanel);
    /////////////////////////////////////////  searchPanel /////////////////////////////////////////
    if (this.display.searchPanel) {
      // if (this.env.config.viewType == "list" && this.context?.default_no_data_v2 != 1) {
      //   if (this.context.splited_tree || this.context.splited_tree_diff_model) {
      //     this.default_no_data_btn = false;
      //   } else {
      //     if (this.context.disable_view_btn) {
      //       this.default_no_data_btn = false;
      //     }
      //     else {
      //       const currentApp = this.menuService.getCurrentApp();
      //       if (currentApp == undefined) {
      //         if (this.context.disable_view_btn) {
      //           this.default_no_data_btn = false;
      //         }
      //         else if (
      //           !this.checkAppIdInTree(
      //             this.menuServices[0],
      //             this.env.config.actionId
      //           ) &&
      //           !this.checkAppIdInTree(
      //             this.menuServices[1],
      //             this.env.config.actionId
      //           ) && !this.checkAppIdInTree(
      //             this.menuServices[2],
      //             this.env.config.actionId
      //           )
      //         )
      //           this.default_no_data_btn = true;
      //       } else if (
      //         currentApp.xmlid != _xmlid[0] &&
      //         currentApp.xmlid != _xmlid[1] &&
      //         currentApp.xmlid != _xmlid[2]
      //       ) {
      //         this.default_no_data_btn = true;
      //       }
      //     }
      //   }
      // }


      this.filters.forEach((filter) => {
        const description = filter.description.toLowerCase();
        if (description === "ship no" || description === "호선번호") {
          this.isShipnoMulti = true;
        } else if (description === "customer" || description === "고객사") {
          this.isCustomerMulti = true;
          this.isHasCustomer = true;
        }
      });
      this.categories.forEach((category) => {
        const description = category.description.toLowerCase();
        if (description === "customer" || description === "고객사") {
          this.isHasCustomer = true;
        }
        if (this.isHasCustomer) return;
      });
      /** @type DomainListRepr */

      //Thay đổi thứ tự này sẽ làm cho các mục của search panel không tự lọc theo domain được
      // this.searchDomain = super._getDomain({ withSearchPanel: false });

      // this.sectionsPromise = await this._fetchSections(
      //   this.categories,
      //   this.filters
      // );
      this.searchDomain = this._getDomain({ withSearchPanel: false });
      this.sectionsPromise = await this._fetchSections(
        this.categories,
        this.filters
      );
      this._setDefaultDateRange(1, false, this.searchDomain);
      // this.searchDomain = this._getDomain({ withSearchPanel: false });
      for (const { fieldName, values } of this.filters) {
        const filterDefaults = searchPanelDefaults[fieldName] || [];
        for (const valueId of filterDefaults) {
          const value = values.get(valueId);
          if (value) {
            value.checked = true;
          }
        }
      }
      // if (
      //   Object.keys(searchPanelDefaults).length ||
      //   this._shouldWaitForData(false)
      // ) {
      // await this.sectionsPromise;
      // }
    }
    this.blockNotification = false;
  },

  getSections(predicate) {
    let sections = [...this.sections.values()].map((section) =>
      Object.assign({}, section, { empty: false })
    );
    if (predicate) {
      sections = sections.filter(predicate);
    }
    return sections.sort((s1, s2) => s1.index - s2.index);
  },

  _calculateDateFromConfig(baseDate, config, isToDate = false) {
    let resultDate = baseDate;

    if (config.day) {
      resultDate = isToDate
        ? resultDate.plus({ days: config.day })
        : resultDate.minus({ days: config.day });
    }
    if (config.week) {
      resultDate = isToDate
        ? resultDate.plus({ weeks: config.week })
        : resultDate.minus({ weeks: config.week });
    }
    if (config.month) {
      resultDate = isToDate
        ? resultDate.plus({ months: config.month })
        : resultDate.minus({ months: config.month });
    }
    if (config.year) {
      resultDate = isToDate
        ? resultDate.plus({ years: config.year })
        : resultDate.minus({ years: config.year });
    }

    return resultDate;
  },

  async _setDefaultDateRange(
    currentId = 1,
    isGetReturn = false,
    domain = [],
    isMonth = false
  ) {
    // Find the production_plan_date category if it exists
    for (const category of this.categories) {

      if (category.click_delete) continue;
      if (isMonth) {
        if (category.widget == "monthpanel") {
          if (category.keys_date_with_context) {
            // Logic cho month widget
            let date_from = null;
            let date_to = null;
            if (category.current === "1") {
              const today = DateTime.local();
              // Mặc định lấy tháng hiện tại: từ đầu tháng đến cuối tháng
              date_from = today.startOf("month");
              date_to = today.endOf("month");
              category.select_month = today;

              // Trigger event
              if (date_from || date_to) {
                const dateValues = {};
                dateValues["from"] = date_from;
                dateValues["to"] = date_to;

                // Only set if we found the date filters
                if (Object.keys(dateValues).length > 0) {
                  category.activeValueId = dateValues;
                  category.date_from = date_from;
                  category.date_to = date_to;
                  category.isShowAllDataBtn = true;

                  if (!isGetReturn) {
                    if (category.date_from) {
                      // Chuyển đổi date_from thành luxon.DateTime
                      const date_from = DateTime.fromISO(category.date_from);
                      if (date_from.isValid) {
                        domain.push([
                          category.fieldName,
                          ">=",
                          serializeDate(date_from),
                        ]);
                      } else {
                        console.error("Invalid date_from:", category.date_from);
                      }
                    }
                    if (category.date_to) {
                      // Chuyển đổi date_to thành luxon.DateTime
                      const date_to = DateTime.fromISO(category.date_to);
                      if (date_to.isValid) {
                        domain.push([
                          category.fieldName,
                          "<=",
                          serializeDate(date_to),
                        ]);
                      } else {
                        console.error("Invalid date_to:", category.date_to);
                      }
                    }
                    continue;
                  }
                }
              }
            }
          }
          // if (!this.searchPanelSelect)
          //   this._notify();
        }
      } else {
        if (/^search_bar(_\d+)?$/.test(category.fieldName)) {
          category.activeSearchBarId = parseInt(currentId);
          if (category.values.size == 2) {
            const options = category.values.get(1).options;
            if (options) {
              for (var index = 0; index < options.length; index++) {
                if (options[index].id === category.activeSearchBarId) {
                  // Calculate dates
                  if (category.keys_date_with_context) {
                    const today = DateTime.local();
                    const field = options[index].field;
                    const dateConfig = category.keys_date_with_context[field];

                    let date_from = null;
                    let date_to = null;

                    // Tính toán date_from (trừ đi)
                    if (dateConfig && dateConfig.from) {
                      date_from = this._calculateDateFromConfig(
                        today,
                        dateConfig.from,
                        false
                      ).startOf("day");
                    }
                    // Tính toán date_to (cộng vào)
                    if (dateConfig && dateConfig.to) {
                      date_to = this._calculateDateFromConfig(
                        today,
                        dateConfig.to,
                        true
                      ).endOf("day");
                    }
                    // Trigger event
                    if (date_from || date_to) {
                      if (!isGetReturn) {
                        category.isShowAllDataBtn = true;
                        const localDate = new Date();
                        category.date_to = date_to;
                        if (date_from) {
                          date_from = date_from.startOf("day").plus({
                            hours: -localDate.getTimezoneOffset() / 60,
                          });
                        }
                        if (date_to) {
                          date_to = date_to.endOf("day").plus({
                            hours: -localDate.getTimezoneOffset() / 60,
                          });
                        }
                        category.date_from = date_from;
                        category.activeValueId = Number(options[index].id);
                        const serialize =
                          field.type === "date"
                            ? serializeDate
                            : serializeDateTime;

                        if (category.date_from) {
                          // Chuyển đổi date_from thành luxon.DateTime
                          const date_from = DateTime.fromISO(
                            category.date_from
                          );
                          if (date_from.isValid) {
                            domain.push([
                              options[index].field,
                              ">=",
                              serialize(date_from),
                            ]);
                          } else {
                            console.error(
                              "Invalid date_from:",
                              category.date_from
                            );
                          }
                        }
                        if (category.date_to) {
                          // Chuyển đổi date_to thành luxon.DateTime
                          if (date_to.isValid) {
                            domain.push([
                              options[index].field,
                              "<=",
                              serialize(date_to),
                            ]);
                          } else {
                            console.error("Invalid date_to:", category.date_to);
                          }
                        }
                      } else {
                        this.env.bus.trigger("SP:DatePanelAutoSet", {
                          id_cate: category.id,
                          date_from: date_from,
                          date_to: date_to,
                        });
                      }
                      if (isGetReturn) return true;
                      else break;
                    }
                    if (isGetReturn) return false;
                    else break;
                  }
                  if (isGetReturn) return false;
                  else break;
                }
              }
            }
          }
        } else if (
          category.widget == "date" ||
          category.widget == "monthpanel"
        ) {
          if (category.keys_date_with_context) {
            if (category.widget == "date") {
              const today = DateTime.local();
              const dateConfig =
                category.keys_date_with_context[category.fieldName];
              let date_from = null;
              let date_to = null;

              // Tính toán date_from (trừ đi)
              if (dateConfig && dateConfig.from) {
                date_from = this._calculateDateFromConfig(
                  today,
                  dateConfig.from,
                  false
                ).startOf("day");
              }
              // Tính toán date_to (cộng vào)
              if (dateConfig && dateConfig.to) {
                date_to = this._calculateDateFromConfig(
                  today,
                  dateConfig.to,
                  true
                ).endOf("day");
              }
              // Trigger event
              if (date_from || date_to) {
                const dateValues = {};
                // category.values = new Map([
                //   [
                //     false,
                //     {
                //       "childrenIds": [],
                //       "display_name": "All",
                //       "id": false,
                //       "bold": true,
                //       "parentId": false
                //     }
                //   ],
                //   [
                //     "from",
                //     {
                //       "id": "from",
                //       "widget": "date",
                //       "op": ">=",
                //       "display_name": "From",
                //       "pro": true,
                //       "field_type": "date",
                //       "childrenIds": [],
                //       "parentId": false,
                //       "pickerOptions": {}
                //     }
                //   ],
                //   [
                //     "to",
                //     {
                //       "id": "to",
                //       "widget": "date",
                //       "op": "<=",
                //       "display_name": "To",
                //       "pro": true,
                //       "field_type": "date",
                //       "childrenIds": [],
                //       "parentId": false,
                //       "pickerOptions": {}
                //     }
                //   ]
                // ])
                category.values.forEach((value, key) => {
                  if (key === "from" && date_from) {
                    dateValues['from'] = date_from;
                  } else if (key === "to" && date_to) {
                    dateValues['to'] = date_to;
                  }
                });
                // Only set if we found the date filters
                if (Object.keys(dateValues).length > 0) {
                  category.activeValueId = dateValues;
                  category.dateValue = dateValues;
                  category.isSearchDefault = true;
                  category.isShowAllDataBtn = true;
                  if (!isGetReturn) {
                    category.values.forEach((value, key) => {
                      if (key) {
                        var date =
                          (category.activeValueId &&
                            category.activeValueId[value.id]) ||
                          (category.dateValue && category.dateValue[key]);
                        if (date) {
                          // Chuyển đổi date thành luxon.DateTime
                          const dateTime = DateTime.fromISO(date);
                          if (dateTime.isValid) {
                            let domainValue = serializeDate(dateTime);
                            category.dateValue[value.id] = dateTime;

                            category.isShowAllDataBtn =
                              category.dateValue?.from ||
                              category.dateValue?.to;
                            domain.push([
                              category.fieldName,
                              value.op,
                              domainValue,
                            ]);
                          } else {
                            console.error("Invalid date:", date);
                          }
                        }
                      }
                    });
                    continue;
                  }
                }
              }
            } else if (category.widget == "monthpanel") {
              // Logic cho month widget
              let date_from = null;
              let date_to = null;
              if (category.current === "1") {
                const today = DateTime.local();
                // Mặc định lấy tháng hiện tại: từ đầu tháng đến cuối tháng
                date_from = today.startOf("month");
                date_to = today.endOf("month");
                category.select_month = today;

                // Trigger event
                if (date_from || date_to) {
                  const dateValues = {};
                  dateValues["from"] = date_from;
                  dateValues["to"] = date_to;

                  // Only set if we found the date filters
                  if (Object.keys(dateValues).length > 0) {
                    category.activeValueId = dateValues;
                    category.date_from = date_from;
                    category.date_to = date_to;
                    category.isShowAllDataBtn = true;

                    if (!isGetReturn) {
                      if (category.date_from) {
                        // Chuyển đổi date_from thành luxon.DateTime
                        const date_from = DateTime.fromISO(category.date_from);
                        if (date_from.isValid) {
                          domain.push([
                            category.fieldName,
                            ">=",
                            serializeDate(date_from),
                          ]);
                        } else {
                          console.error(
                            "Invalid date_from:",
                            category.date_from
                          );
                        }
                      }
                      if (category.date_to) {
                        // Chuyển đổi date_to thành luxon.DateTime
                        const date_to = DateTime.fromISO(category.date_to);
                        if (date_to.isValid) {
                          domain.push([
                            category.fieldName,
                            "<=",
                            serializeDate(date_to),
                          ]);
                        } else {
                          console.error("Invalid date_to:", category.date_to);
                        }
                      }
                      continue;
                    }
                  }
                }
              }
            }
          }
          // if (!this.searchPanelSelect)
          // this._notify();
        }
      }
    }
    return false;
  },

  async _fetchSections(categoriesToLoad, filtersToLoad) {
    // if (this.context.default_no_data_btn) {
    //   if (this.can_reload_section == true) {
    //     if (
    //       !this.context?.splited_tree_diff_model &&
    //       !this.context?.splited_tree &&
    //       !this.env.inDialog
    //     ) {
    //       if (this.search_panel_follows.getActionId() !== this.searchViewId) {
    //         this.is_diff_action = true;
    //         this.search_panel_follows.updateActionId(this.searchViewId);
    //       }
    //       if (this.is_diff_action) {
    //         this.search_panel_follows.clearFollows();
    //         this.search_panel_follows.clearDateSearch();
    //       }
    //     } else if (
    //       !this.context?.splited_tree_diff_model &&
    //       !this.context?.splited_tree &&
    //       !this.env.inDialog
    //     ) {
    //       this.search_panel_follows.clearDateSearch();
    //     }
    //     await super._fetchSections(categoriesToLoad, filtersToLoad);
    //     this.can_reload_section = false
    //   }
    // }
    // else {
    if (this.resModel.startsWith("document")) {

      return super._fetchSections(...arguments);
    }
    if (
      !this.context?.splited_tree_diff_model &&
      !this.context?.splited_tree &&
      !this.env.inDialog
    ) {
      if (this.search_panel_follows.getActionId() !== this.searchViewId) {
        this.is_diff_action = true;
        this.search_panel_follows.updateActionId(this.searchViewId);
      }
      if (this.is_diff_action) {
        this.search_panel_follows.clearFollows();
        this.search_panel_follows.clearDateSearch();
      }
    } else if (
      !this.context?.splited_tree_diff_model &&
      !this.context?.splited_tree &&
      !this.env.inDialog
    ) {
      this.search_panel_follows.clearDateSearch();
    }
    await super._fetchSections(categoriesToLoad, filtersToLoad);
    // }
  },

  getDomainForShipNo(description) {
    let customer_names = [];
    let domain = [];
    if (description === "ship no" || description === "호선번호") {
      if (this.isHasCustomer) {
        if (this.isCustomerMulti)
          customer_names = this.search_panel_follows.getAllCustomerName();
        else customer_names = [this.search_panel_follows.getCustomerName()];
        customer_names.forEach((customer_name) => {
          if (customer_name == "HMD" || customer_name == "현대미포조선")
            domain.push(["name_length", "=", 6]);
          else if (customer_name == "HHI" || customer_name == "현대중공업")
            domain.push(["name_length", "=", 4]);
        });
        if (domain.length == 2) {
          domain = ["|", ...domain];
        }
        if (domain.length > 0) {
        }
      }
    }
    return domain;
  },

  /**
   * Fetches values for each filter. This is done at startup and at each
   * reload if needed.
   * @param {Filter[]} filters
   * @returns {Promise} resolved when all filters have been fetched
   */
  async _fetchFilters(filters) {
    if (this.resModel.startsWith("document"))
      return await super._fetchFilters(filters);
    // if (this.isFetchFillter) return;
    // this.isFetchFillter = true;
    const evalContext = {};
    for (const category of this.categories) {
      evalContext[category.fieldName] = category.activeValueId;
    }
    const categoryDomain = this._getCategoryDomain();
    const searchDomain = this.searchDomain;
    await Promise.all(
      filters.map(async (filter) => {
        let domain = this.getDomainForShipNo(filter.description.toLowerCase());
        const result = await this.orm.call(
          this.resModel,
          "search_panel_select_multi_range",
          [filter.fieldName],
          {
            category_domain: categoryDomain,
            domain: [...super._getDomain(), ...domain],
            comodel_domain: [
              ...new Domain(filter.domain).toList(evalContext),
              ...domain,
            ],
            context: this.globalContext,
            enable_counters: filter.enableCounters,
            filter_domain: this._getFilterDomain(filter.id),
            expand: filter.expand,
            group_by: filter.groupBy || false,
            group_domain: this._getGroupDomain(filter),
            limit: filter.limit,
            search_domain: searchDomain,
            search_domain_temp: this.searchDomainTemp,
          }
        );
        this._createFilterTree(filter.id, result);
      })
    );
  },

  async _fetchFiltersShipNo(filters, customer_name = "") {
    const evalContext = {};
    for (const category of this.categories) {
      evalContext[category.fieldName] = category.activeValueId;
    }
    const categoryDomain = this._getCategoryDomain();
    const searchDomain = this.searchDomain;
    await Promise.all(
      filters.map(async (filter) => {
        const description = filter.description.toLowerCase();
        if (description === "ship no" || description === "호선번호") {
          let domain = this.getDomainForShipNo(description);
          const result = await this.orm.call(
            this.resModel,
            "search_panel_select_multi_range",
            [filter.fieldName],
            {
              category_domain: categoryDomain,
              comodel_domain: [
                ...new Domain(filter.domain).toList(evalContext),
                ...domain,
              ],
              context: this.globalContext,
              enable_counters: filter.enableCounters,
              filter_domain: this._getFilterDomain(filter.id),
              expand: this.default_no_data_btn || filter.expand,
              group_by: filter.groupBy || false,
              group_domain: this._getGroupDomain(filter),
              limit: filter.limit,
              search_domain: searchDomain,
            }
          );
          this._createFilterTree(filter.id, result);
        }
      })
    );
  },
  async _fetchCategories(categories) {
    if (this.resModel.startsWith("document"))
      return await super._fetchCategories(categories);
    const filterDomain = this._getFilterDomain();
    const searchDomain = this.searchDomain;
    const evalContext = {};

    for (const category of this.categories) {
      evalContext[category.fieldName] = category.activeValueId;
    }
    await Promise.all(
      categories.map(async (category) => {
        if (/^search_bar(_\d+)?$/.test(category.fieldName)) {
          if (this.isFetchSearchBar) return;
          this.isFetchSearchBar = true;
        }
        const description = category.description.toLowerCase();

        let domain = this.getDomainForShipNo(
          category.description.toLowerCase()
        );
        const category_domain = this._getCategoryDomain(category.id);
        const result = await this.orm.call(
          this.resModel,
          "search_panel_select_range",
          [category.fieldName],
          {
            model: this.resModel,
            description,
            category_domain: category_domain,
            domain: [...super._getDomain(), ...domain, ...this.searchDomain],
            context: { ...this.globalContext, ...category.context },
            enable_counters: category.enableCounters,
            expand: category.expand,
            comodel_domain: [
              ...new Domain(category.domain).toList(evalContext),
              ...domain,
            ],
            filter_domain: filterDomain,
            hierarchize: category.hierarchize,
            limit: category.limit,
            search_type: category.searchType,
            search_domain: searchDomain,
            search_domain_temp: this.searchDomainTemp,
          }
        );
        this._createCategoryTree(category.id, result);
        if (category.widget === "monthpanel") {
          category.activeValueId = true;
        }
      })
    );
  },

  async _fetchCategoriesForShipNo(categories, customer_name = "") {
    const filterDomain = this._getFilterDomain();
    const searchDomain = this.searchDomain;
    const evalContext = {};
    for (const category of this.categories) {
      evalContext[category.fieldName] = category.activeValueId;
    }
    await Promise.all(
      categories.map(async (category) => {
        const description = category.description.toLowerCase();

        if (description === "ship no" || description === "호선번호") {
          let domain = this.getDomainForShipNo(description);
          const category_domain = this._getCategoryDomain(category.id);
          const result = await this.orm.call(
            this.resModel,
            "search_panel_select_range",
            [category.fieldName],
            {
              model: this.resModel,
              description,
              domain: super._getDomain(),
              category_domain: category_domain,
              context: { ...this.globalContext, ...category.context },
              enable_counters: category.enableCounters,
              expand: category.expand,
              comodel_domain: [
                ...new Domain(category.domain).toList(evalContext),
                ...domain,
              ],
              filter_domain: filterDomain,
              hierarchize: category.hierarchize,
              limit: category.limit,
              search_type: category.searchType,
              search_domain: searchDomain,
            }
          );
          this._createCategoryTree(category.id, result);
        }
      })
    );
  },

  //Build fields such as date, bool, etc.
  async _createCategoryTree(sectionId, result) {
    if (this.resModel.startsWith("document"))
      return await super._createCategoryTree(sectionId, result);
    let category = await this.sections.get(sectionId);
    const field = this.searchViewFields[category.fieldName];
    category.fieldType = field.type;
    category.keys_date_with_context = result.keys_date_with_context ?? {};
    category.widget = result.widget ?? "";
    //Handle special types

    const description = category.description.toLowerCase();
    if (
      ["integer", "float", "monetary", "boolean", "date", "datetime"].includes(
        field.type
      )
    )
      category.pro = true;

    if (field.type === "selection" && /^search_bar(_\d+)?$/.test(field.name)) {
      const options = field.selection.map(([field, display_name], index) => ({
        id: index + 1,
        display_name,
        field,
      }));

      result.values = [
        {
          id: 1,
          display_name: "",
          parentId: false,
          childrenIds: [],
          parentId: false,
          widget: "datepanel",
          options: options,
        },
      ];


    }
    else if (field.type === "selection" && !/^search_bar(_\d+)?$/.test(field.name)) {
      let options = result.values;
      var default_id = 1;

      // === BẮT ĐẦU CODE MỚI: Đọc cờ 'selected' từ Python ===

      // Tìm xem trong options có cái nào được Python đánh dấu selected = true không
      const serverSelectedOption = options.find(opt => opt.selected === true);
      if (serverSelectedOption && !category.userManuallyCleared) {
        // ... (Code gán giá trị và push domain giữ nguyên) ...
        category.activeValueId = serverSelectedOption.id;
        default_id = serverSelectedOption.id;

        // Kiểm tra tránh duplicate trước khi push
        const alreadyInDomain = this.searchDomain.some(d => d[0] === category.fieldName && d[2] === category.activeValueId);
        if (!alreadyInDomain) {
          this.searchDomain.push([category.fieldName, "=", category.activeValueId]);
        }
        category.displayValue = serverSelectedOption.display_name;
        category.isShowAllDataBtn = true;
        category.userManuallyCleared = true; // Đánh dấu đã thiết lập từ server
      }
    }
    else if (
      (category.fieldType === "many2one" ||
        category.fieldType === "many2many")
    ) {
      let options = result.values;
      var default_id = 1;

      // === BẮT ĐẦU CODE MỚI: Đọc cờ 'selected' từ Python ===

      // Tìm xem trong options có cái nào được Python đánh dấu selected = true không
      const serverSelectedOption = options.find(opt => opt.selected === true);
      if (serverSelectedOption && !category.userManuallyCleared) {
        // ... (Code gán giá trị và push domain giữ nguyên) ...
        category.activeValueId = serverSelectedOption.id;
        default_id = serverSelectedOption.id;

        // Kiểm tra tránh duplicate trước khi push
        const alreadyInDomain = this.searchDomain.some(d => d[0] === category.fieldName && d[2] === category.activeValueId);
        if (!alreadyInDomain) {
          this.searchDomain.push([category.fieldName, "=", category.activeValueId]);
        }
        category.displayValue = serverSelectedOption.display_name;
        category.userManuallyCleared = true; // Đánh dấu đã thiết lập từ server
      }

      // === KẾT THÚC CODE MỚI ===

      if (this.env.inDialog) {
        const activeValueId =
          this.search_panel_follows.findFollowByDescription(description);

        if (activeValueId) {
          default_id = activeValueId;
          category.activeValueId = activeValueId;
          this.searchDomain.push([
            category.fieldName,
            "=",
            category.activeValueId,
          ]);
        }
      }
      else if (
        this.context?.splited_tree ||
        this.context?.splited_tree_diff_model
      ) {
        default_id = 1;
      } else {
        if (description === "customer" || description === "고객사") {
          const idCustomer = this.search_panel_follows.getIdCustomerFollow();
          if (idCustomer != 0) {
            default_id = idCustomer;
            category.activeValueId = idCustomer;

          }
        } else {
          if (category.follow == "1") {
            const activeValueId =
              this.search_panel_follows.findFollowByDescription(description);
            if (activeValueId) {
              default_id = activeValueId;
              category.activeValueId = activeValueId;
              this.searchDomain.push([
                category.fieldName,
                "=",
                category.activeValueId,
              ]);
            }
          }
        }
      }
      // Create an empty option
      const emptyOption = {
        id: "",
        display_name: "Select",
        parentId: false,
      };
      options?.unshift(emptyOption);
      result.values = [
        {
          id: default_id,
          display_name: "",
          parentId: false,
          current_selected: category.activeValueId, //can  de build domain
          childrenIds: [],
          activeValueId: category.activeValueId,
          widget: "combobox",
          options: options,
        },
      ];
    }

    //end Special handling
    let { error_msg, parent_field: parentField, values, fieldType } = result;
    if (error_msg) {
      category.errorMsg = error_msg;
      values = [];
    }
    if (category.hierarchize) {
      category.parentField = parentField;
    }

    if (
      (fieldType == "many2one" || fieldType == "many2many") &&
      !this.resModel.startsWith("document")

    ) {
      for (const value of result.values) {
        category.values.set(value.id, value);
      }
    } else {
      for (const value of values) {
        //todo:Processing date type, reference <input data-toggle="datetimepicker" data-date-format="YYYY-MM-DD" placeholder="start date" />
        if (value.widget === "date" && value.id) {
          category.values.set(
            value.id,
            Object.assign({}, value, {
              widget: "date",
              childrenIds: [],
              parentId: value[parentField] || false,
              pickerOptions: {},
            })
          );
        } else if (value.widget === "monthpanel" && value.id) {
          category.values.set(
            value.id,
            Object.assign({}, value, {
              widget: "monthpanel",
              childrenIds: [],
              parentId: value[parentField] || false,
              pickerOptions: {},
            })
          );
        } else if (value.widget === "yearpanel" && value.id) {
          category.values.set(
            value.id,
            Object.assign({}, value, {
              widget: "yearpanel",
              childrenIds: [],
              parentId: value[parentField] || false,
              pickerOptions: {},
            })
          );
        } else if (value.widget === "boolean" && value.id)
          category.values.set(
            value.id,
            Object.assign({}, value, {
              childrenIds: [],
              parentId: value[parentField] || false,
              activeValueId: undefined,
            })
          );
        else
          category.values.set(
            value.id,
            Object.assign({}, value, {
              childrenIds: [],
              parentId: value[parentField] || false,
            })
          );
      }
    }

    for (const value of values) {
      const { parentId } = category?.values.get(value.id);
      if (parentId && category.values.has(parentId)) {
        category.values.get(parentId).childrenIds.push(value.id);
      }
    }
    // collect rootIds
    category.rootIds = [false];
    for (const value of values) {
      const { parentId } = category.values?.get(value.id);
      if (!parentId) {
        category.rootIds.push(value.id);
      }
    }
    // Set active value from context
    const valueIds = [
      false,
      ...values.map((val) => val.current_selected ?? val.id),
    ];

    this._ensureCategoryValue(category, valueIds);
  },

  _createFilterTree(sectionId, result) {
    const filter = this.sections.get(sectionId);

    let { error_msg, values } = result;
    if (error_msg) {
      filter.errorMsg = error_msg;
      values = [];
    }

    // 🔥 THAY ĐỔI: restore checked property hoặc dùng giá trị từ backend
    values.forEach((value) => {
      const oldValue = filter.values.get(value.id);
      // 🔥 Ưu tiên: oldValue.checked → value.checked từ backend → false
      value.checked = oldValue ? oldValue.checked : (value.checked || false);
    });

    filter.values = new Map();
    const groupIds = [];
    if (filter.groupBy) {
      const groups = new Map();
      for (const value of values) {
        const groupId = value.group_id;
        if (!groups.has(groupId)) {
          if (groupId) {
            groupIds.push(groupId);
          }
          groups.set(groupId, {
            id: groupId,
            name: value.group_name,
            values: new Map(),
            tooltip: value.group_tooltip,
            sequence: value.group_sequence,
            color_index: value.color_index,
          });
          // restore former checked state
          const oldGroup = filter.groups && filter.groups.get(groupId);
          groups.get(groupId).state = (oldGroup && oldGroup.state) || false;
        }
        groups.get(groupId).values.set(value.id, value);
      }
      filter.groups = groups;
      filter.sortedGroupIds = sortBy(
        groupIds,
        (id) => groups.get(id).sequence || groups.get(id).name
      );
      for (const group of filter.groups.values()) {
        for (const [valueId, value] of group.values) {
          filter.values.set(valueId, value);
        }
      }
    } else {
      for (const value of values) {
        filter.values.set(value.id, value);
      }
    }
  },

  _ensureCategoryValue(category, valueIds) {
    if (!valueIds.includes(category.activeValueId)) {
      //boolean special treatment
      if (category.fieldType == "boolean") category.activeValueId = undefined;
      else {
        category.activeValueId = valueIds[0];
      }
    }
  },

  onDateTimeChanged(section, value, date) {
    if (value.widget == "date" && date) {
      if (section.activeValueId[value.id] !== date) {
        let obj = {};
        obj[value.id] = date;
        this.env.searchModel.toggleCategoryValue(category.id, obj);
      }
    }
  },

  async toggleCategoryValue(
    sectionId,
    valueId,
    select_month = undefined,
    is_clear_date = false
  ) {
    if (this.resModel.startsWith("document")) {
      return super.toggleCategoryValue(...arguments);
    }
    if (this.default_no_data_btn) {
      localStorage.setItem("N:CanLoad", 1);
    }
    this.searchPanelSelect = true;
    let is_search_bar = false;

    const category = this.sections.get(sectionId);
    console.log("category:", category);
    category.select_month = select_month;
    if (["date", "datetime"].includes(category.fieldType)) {
      if (valueId === undefined || !category.activeValueId) {
        category.activeValueId = undefined;
        category.click_delete = true;
        category.dateValue = undefined;
        if (is_clear_date) category.dateValueTemp = undefined;
      } else {
        category.activeValueId = Object.assign(category.activeValueId, valueId);
      }

      if (category.searchType == "month") {
        if (valueId !== undefined) {
          category.click_delete = true;
          category.activeValueId = Number(valueId["month"].value_id);
          category.date_from = valueId["month"].date_from;
          category.date_to = valueId["month"].date_to;
        } else {
          category.click_delete = true;
          category.date_from = undefined;
          category.date_to = undefined;
        }
      } else if (category.searchType == "year") {
        if (valueId !== undefined) {
          category.activeValueId = Number(valueId["year"].value_id);
          category.date_from = valueId["year"].date_from;
          category.date_to = valueId["year"].date_to;
        } else {
          category.click_delete = true;
          category.date_from = undefined;
          category.date_to = undefined;
        }
      }

      // this.search_panel_follows.addDateSearch(
      //   category.fieldName.toLowerCase(),
      //   category.activeValueId
      // );
    } else if ("boolean" === category.fieldType) {
      category.activeValueId = valueId;
    } else if (["integer", "float", "monetary"].includes(category.fieldType)) {
      if (valueId === undefined || !category.activeValueId)
        category.activeValueId = valueId;
      else
        category.activeValueId = Object.assign(category.activeValueId, valueId);
    } else if (["many2many", "many2one"].includes(category.fieldType)) {
      if (valueId == undefined) {
        //click button reset
        category.activeValueId = false;
        category.current_selected = {};
        category.userManuallyCleared = true;
      } else {
        category.activeValueId = Number(valueId[1]);
        category.current_selected = valueId;
      }
      const description_lower = category.description.toLowerCase();

      if (description_lower === "customer" || description_lower === "고객사") {
        category.values.forEach((value) => {
          if (value.options) {
            category.displayValue = value.options.find(
              (item) => item.id === category.activeValueId
            )?.display_name;
          }
        });
        this.search_panel_follows.updateIdCustomerFollow(
          category.activeValueId,
          category.displayValue
        );
        // if (this.context?.search_panel_by_parent === undefined || this.context?.search_panel_by_parent === false) {
        //   if (this.isShipnoMulti) {
        //     await this._fetchFiltersShipNo(this.filters, category.displayValue);
        //   }
        //   else
        //     await this._fetchCategoriesForShipNo(this.categories, category.displayValue);
        // }
      }
      // if (this.context?.search_panel_by_parent) {
      // await this._fetchCategories(this.categories);
      // }
    } else if (
      "selection" === category.fieldType &&
      /^search_bar(_\d+)?$/.test(category.fieldName)
    ) {
      is_search_bar = true;

      if (valueId == undefined) {
        category.click_delete = true;
        //click button reset
        // this.search_panel_follows.addDateSearch(
        //   category.values
        //     .get(1)
        //     .options.find((item) => item.id === category.activeValueId)
        //     ?.field.toLowerCase(),
        //   { from: undefined, to: undefined }
        // );
        category.activeValueId = false;
        category.date_from = false;
        category.date_to = false;
      } else {
        category.activeValueId = Number(valueId[1].value_id);
        category.date_from = valueId[1].date_from;
        category.date_to = valueId[1].date_to;
        // this.search_panel_follows.addDateSearch(
        //   category.values
        //     .get(1)
        //     .options.find((item) => item.id === category.activeValueId)
        //     ?.field.toLowerCase(),
        //   { from: category.date_from, to: category.date_to }
        // );

        // const { from_date, to_date } = this.search_panel_follows.getDateSearch('start_date')
        // let domain = []
        // if (from_date)
        //   domain.push(['start_date', '>=', from_date.toFormat('yyyy-MM-dd HH:mm:ss')])
        // if (to_date)
        //   domain.push(['start_date', '>=', to_date.toFormat('yyyy-MM-dd HH:mm:ss')])
        // console.log('domain', domain)
      }
    } else {

      category.activeValueId = valueId;
      category.userManuallyCleared = true;

    }
    if (
      ("selection" === category.fieldType &&
        /^search_bar(_\d+)?$/.test(category.fieldName)) ||
      category.widget === "monthpanel" ||
      category.widget === "yearpanel"
    )
      category.isShowAllDataBtn =
        category.activeValueId !== false && category.activeValueId !== undefined
          ? category.date_from || category.date_to
          : false;
    else if (category.widget === "date") {
      if (valueId) {
        category.dateValueTemp = deepCopy({
          ...category.dateValueTemp,
          ...valueId,
        });
        category.dateValue = { ...category.dateValueTemp, ...valueId };
      }
      category.isShowAllDataBtn =
        category.dateValue?.from || category.dateValue?.to;
    } else
      category.isShowAllDataBtn =
        category.activeValueId !== false && category.activeValueId !== undefined
          ? true
          : false;
    this._notify(is_search_bar);

    if (
      this.context?.splited_tree_diff_model ||
      this.context?.splited_tree ||
      this.env.inDialog
    )
      return;

    if (category.follow === "1") {
      this.search_panel_follows.addFollow(
        category.description.toLowerCase(),
        category.activeValueId
      );
    }
  },

  async toggleFilterValues(sectionId, valueIds, forceTo = null) {
    if (this.default_no_data_btn) {
      localStorage.setItem("N:CanLoad", 1);
    }
    this.searchPanelSelect = true;
    const filter = this.sections.get(sectionId);
    let value;
    for (const valueId of valueIds) {
      value = filter.values.get(valueId);
      value.checked = forceTo === null ? !value.checked : forceTo;
    }
    const description_lower = filter.description.toLowerCase();
    if (description_lower === "customer" || description_lower === "고객사") {
      this.search_panel_follows.updateIdCustomerFollowFilter(value);
      // if (this.isShipnoMulti) {
      //   await this._fetchFiltersShipNo(this.filters);
      // }
      // else
      //   await this._fetchCategoriesForShipNo(this.categories);
    }
    this._notify();
    if (
      this.context?.splited_tree_diff_model ||
      this.context?.splited_tree ||
      this.env.inDialog
    )
      return;

    if (filter.follow === "1") {
      this.search_panel_follows.addFollowFilter(
        filter.description.toLowerCase(),
        value
      );
    }
  },

  _getCategoryDomain(excludedCategoryId) {
    const domain = [];
    for (const category of this.categories) {
      if (
        category.id === excludedCategoryId ||
        (category.fieldType != "boolean" &&
          !category.activeValueId &&
          category.dateValue &&
          Object.keys(category.dateValue).length === 0)
      ) {
        continue;
      }

      const field = this.searchViewFields[category.fieldName];
      const operator =
        field.type === "many2one" && category.parentField ? "child_of" : "=";
      if (category.activeValueId && this.resModel.startsWith("document")) {
        // check if category.activeValuIde  is dict
        const activeValueId = category.activeValueId;

        if (
          activeValueId !== null &&
          typeof activeValueId === "object" &&
          activeValueId.constructor === Object
        ) {
          domain.push([category.fieldName, "=", Number(activeValueId[1])]);
        } else {
          domain.push([category.fieldName, "=", activeValueId]);
        }
      } else if (field.type === "date" || field.type === "datetime") {
        if (category.searchType == "month") {
          if (category.date_from) {
            // Chuyển đổi date_from thành luxon.DateTime
            const date_from = DateTime.fromISO(category.date_from);
            if (date_from.isValid) {
              domain.push([category.fieldName, ">=", serializeDate(date_from)]);
            } else {
              console.error("Invalid date_from:", category.date_from);
            }
          }
          if (category.date_to) {
            // Chuyển đổi date_to thành luxon.DateTime
            const date_to = DateTime.fromISO(category.date_to);
            if (date_to.isValid) {
              domain.push([category.fieldName, "<=", serializeDate(date_to)]);
            } else {
              console.error("Invalid date_to:", category.date_to);
            }
          }
        } else if (category.searchType == "year") {
          if (category.date_from) {
            // Chuyển đổi date_from thành luxon.DateTime
            const date_from = DateTime.fromISO(category.date_from);
            if (date_from.isValid) {
              domain.push([category.fieldName, ">=", serializeDate(date_from)]);
            } else {
              console.error("Invalid date_from:", category.date_from);
            }
          }
          if (category.date_to) {
            // Chuyển đổi date_to thành luxon.DateTime
            const date_to = DateTime.fromISO(category.date_to);
            if (date_to.isValid) {
              domain.push([category.fieldName, "<=", serializeDate(date_to)]);
            } else {
              console.error("Invalid date_to:", category.date_to);
            }
          }
        } else {
          category.values.forEach((value, key) => {
            if (key) {
              var date =
                (category.activeValueId && category.activeValueId[value.id]) ||
                (category.dateValue && category.dateValue[key]);
              if (date) {
                // Chuyển đổi date thành luxon.DateTime
                const dateTime = DateTime.fromISO(date);
                if (dateTime.isValid) {
                  let domainValue = serializeDate(dateTime);
                  category.dateValue[value.id] = dateTime;

                  category.isShowAllDataBtn =
                    category.dateValue?.from || category.dateValue?.to;
                  domain.push([category.fieldName, value.op, domainValue]);
                } else {
                  console.error("Invalid date:", date);
                }
              }
            }
          });
        }
      } else if (["integer", "float", "monetary"].includes(field.type)) {
        category.values.forEach((value, key) => {
          if (key) {
            var val = category.activeValueId[value.id];
            if (val) {
              domain.push([category.fieldName, value.op, val]);
            }
          }
        });
      } else if (["boolean"].includes(field.type)) {
        if (category.activeValueId != undefined)
          domain.push([category.fieldName, "=", category.activeValueId]);
      } else if (["many2many", "many2one"].includes(field.type)) {
        if (category.activeValueId != undefined)
          domain.push([category.fieldName, "=", category.activeValueId]);
      }
      //date panel group
      else if (
        field.type == "selection" &&
        /^search_bar(_\d+)?$/.test(field.name)
      ) {
        const options = Array.from(category.values.values())[1].options;
        const option = options.find(
          (option) => option.id === category.activeValueId
        );
        const serialize =
          field.type === "date" ? serializeDate : serializeDateTime;
        if (
          category.date_from &&
          category.date_from?.isLuxonDateTime == undefined
        )
          category.date_from = DateTime.fromISO(category.date_from);
        if (category.date_to && category.date_to?.isLuxonDateTime == undefined)
          category.date_to = DateTime.fromISO(category.date_to);
        if (category.date_from) {
          // Chuyển đổi date_from thành luxon.DateTime
          const date_from = DateTime.fromISO(category.date_from);
          if (date_from.isValid) {
            domain.push([option.field, ">=", serialize(category.date_from)]);
          } else {
            console.error("Invalid date_from:", category.date_from);
          }
        }
        if (category.date_to) {
          // Chuyển đổi date_to thành luxon.DateTime
          const date_to = DateTime.fromISO(category.date_to);
          if (date_to.isValid) {
            const localDate = new Date();

            domain.push([
              option.field,
              "<=",
              serialize(
                category.date_to
                  .endOf("day")
                  .plus({ hours: -localDate.getTimezoneOffset() / 60 })
              ),
            ]);
          } else {
            console.error("Invalid date_to:", category.date_to);
          }
        }
      } else
        domain.push([category.fieldName, operator, category.activeValueId]);
      //for dms module
      if (domain.length === 0 && this.resModel.startsWith("document")) {
        domain.push([category.fieldName, "=", false]);
      }
    }
    return domain;
  },

  //    todo: 以上后续移到 基础

  //    todo: 搜索用 and，此处重写方法，后续super
  _getGroups() {
    const preGroups = [];
    for (const queryElem of this.query) {
      const { searchItemId } = queryElem;
      let { groupId } = this.searchItems[searchItemId];
      if ("autocompleteValue" in queryElem) {
        if (queryElem.autocompleteValue.isShiftKey) {
          groupId = Math.random();
        }
      }
      let preGroup = preGroups.find((group) => group.id === groupId);
      if (!preGroup) {
        preGroup = { id: groupId, queryElements: [] };
        preGroups.push(preGroup);
      }
      queryElem.groupId = groupId;
      preGroup.queryElements.push(queryElem);
    }
    const groups = [];
    for (const preGroup of preGroups) {
      const { queryElements, id } = preGroup;
      const activeItems = [];
      for (const queryElem of queryElements) {
        const { searchItemId } = queryElem;
        let activeItem = activeItems.find(
          ({ searchItemId: id }) => id === searchItemId
        );
        if ("generatorId" in queryElem) {
          if (!activeItem) {
            activeItem = { searchItemId, generatorIds: [] };
            activeItems.push(activeItem);
          }
          activeItem.generatorIds.push(queryElem.generatorId);
        } else if ("intervalId" in queryElem) {
          if (!activeItem) {
            activeItem = { searchItemId, intervalIds: [] };
            activeItems.push(activeItem);
          }
          activeItem.intervalIds.push(queryElem.intervalId);
        } else if ("autocompleteValue" in queryElem) {
          if (!activeItem) {
            activeItem = { searchItemId, autocompletValues: [] };
            activeItems.push(activeItem);
          }
          activeItem.autocompletValues.push(queryElem.autocompleteValue);
        } else if (!activeItem) {
          activeItem = { searchItemId };
          activeItems.push(activeItem);
        }
      }
      for (const activeItem of activeItems) {
        if ("intervalIds" in activeItem) {
          activeItem.intervalIds.sort(
            (g1, g2) => rankInterval(g1) - rankInterval(g2)
          );
        }
      }
      groups.push({ id, activeItems });
    }

    return groups;
  },

  deactivateGroup(groupId) {
    this.query = this.query.filter((queryElem) => {
      return queryElem.groupId !== groupId;
    });

    for (const partName in this.domainParts) {
      const part = this.domainParts[partName];
      if (part.groupId === groupId) {
        this.setDomainParts({ [partName]: null });
      }
    }
    this._checkComparisonStatus();
    this._notify();
  },
});
